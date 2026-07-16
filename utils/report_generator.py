"""Generate an Annexure I-aligned BRSR Core PDF without external ReportLab."""

from datetime import date

from fpdf import FPDF, FontFace

from utils.calculations import (
    calculate_accounts_payable_days, calculate_energy_metrics,
    calculate_gender_metrics, calculate_ghg_intensity, calculate_inclusive_dev,
    calculate_all, calculate_ltifr, calculate_rpt_shares, calculate_water_metrics,
    calculate_waste_metrics,
)


NAVY = (0, 45, 98)
LIGHT_BLUE = (234, 242, 248)


def _number(value, decimals=2):
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "Not reported"


class BRSRPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*NAVY)
        self.cell(0, 6, "BRSR CORE REPORT - ANNEXURE I ALIGNED", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*NAVY)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(7)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, "Generated from the BRSR Core application", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")


def _table(pdf, headers, rows, widths):
    """Render a compact table with fpdf2's table layout engine."""
    pdf.set_font("Helvetica", size=7.1)
    headings = FontFace(emphasis="B", color=255, fill_color=NAVY, size_pt=7.1)
    with pdf.table(
        headings_style=headings,
        col_widths=widths,
        line_height=4.6,
        text_align=("CENTER", "LEFT", "LEFT", "LEFT", "RIGHT", "LEFT"),
        borders_layout="ALL",
        first_row_as_headings=True,
        width=pdf.epw,
    ) as table:
        row = table.row()
        for value in headers:
            row.cell(value)
        for data in rows:
            row = table.row()
            for value in data:
                row.cell(str(value))


def _section_title(pdf, title):
    pdf.set_text_color(*NAVY)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)


def build_brsr_core_pdf(state):
    """Return an Annexure I-aligned BRSR Core report as bytes.

    It uses only fpdf2, already listed in this project's requirements, so the
    Streamlit Export page does not depend on ReportLab.
    """
    revenue = float(state.get("revenue") or 0)
    denominator = revenue or 1.0
    computed = calculate_all(state)
    ghg = calculate_ghg_intensity(state.get("scope1", 0), state.get("scope2", 0), denominator, 1.0)
    water = calculate_water_metrics(state.get("input_m", 0), state.get("output_m", 0), denominator, 1.0)
    energy = calculate_energy_metrics(state.get("renewable", 0), state.get("non_renewable", 0), denominator, 1.0)
    waste_keys = ("waste_plastic", "waste_e", "waste_bio", "waste_cd", "waste_battery", "waste_radio", "waste_haz", "waste_nonhaz")
    waste = calculate_waste_metrics([state.get(key, 0) for key in waste_keys], state.get("waste_recovered", 0), denominator, 1.0)
    ltifr = calculate_ltifr(state.get("lti_count", 0), state.get("working_hours", 1000000))
    gender = calculate_gender_metrics(state.get("female_wages", 0), state.get("total_wages", 0) or 1)
    inclusive = calculate_inclusive_dev(state.get("msme_proc", 0), state.get("total_proc", 0) or 1, state.get("rural_wages", 0), state.get("semi_urban_wages", 0), state.get("total_wages", 0) or 1)
    ap_days = calculate_accounts_payable_days(state.get("accounts_payable", 0), state.get("cost_procured", 0) or 1)
    rpt = calculate_rpt_shares(state.get("rpt_pur", 0), state.get("tot_pur", 0) or 1, state.get("rpt_sal", 0), state.get("tot_sal", 0) or 1, 0, 1, 0, 1)

    pdf = BRSRPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_title("BRSR Core Report")
    pdf.set_author("BRSR Core application")
    pdf.add_page()
    pdf.ln(13)
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "BUSINESS RESPONSIBILITY AND SUSTAINABILITY REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(77, 89, 102)
    pdf.cell(0, 6, "BRSR Core - Annexure I reporting matrix", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)
    _section_title(pdf, "SECTION A: GENERAL DISCLOSURES")
    general = [
        ("Corporate Identity Number (CIN)", state.get("cin") or "Not reported", "Financial year for reporting", state.get("financial_year") or "Not reported"),
        ("Name of listed entity", state.get("entity_name") or "Not reported", "Year of incorporation", state.get("inc_year") or "Not reported"),
        ("Reporting boundary", state.get("boundary") or "Not reported", "Paid-up capital", f"INR {_number(state.get('paid_up_capital', 0))}"),
        ("Total turnover / revenue", f"INR {_number(revenue)}", "Physical output", f"{_number(state.get('physical_output_quantity', 0), 4)} {state.get('physical_output_unit') or 'Unit'}"),
        ("Type of assurance obtained", state.get("assurance_type") or "None", "", ""),
        ("Report generation date", date.today().isoformat(), "", ""),
    ]
    pdf.set_font("Helvetica", size=8)
    widths = (50, 85, 50, 85)
    for line in general:
        for index, value in enumerate(line):
            pdf.set_fill_color(*(LIGHT_BLUE if index in (0, 2) else (255, 255, 255)))
            pdf.set_font("Helvetica", "B" if index in (0, 2) else "", 8)
            pdf.cell(widths[index], 9, str(value), border=1, fill=True)
        pdf.ln()
    pdf.ln(7)
    pdf.set_font("Helvetica", size=8.5)
    pdf.multi_cell(0, 5, "This report presents fields captured in the application in an Annexure I-aligned reporting matrix. Any disclosure not collected by the application must be completed and independently assured, where applicable, before regulatory filing.")

    headers = ["Sr. No.", "Attribute", "Parameter", "Measurement", "Current FY value", "Cross-reference to BRSR"]
    table_widths = (5, 17, 31, 16, 15, 20)
    pdf.add_page()
    _section_title(pdf, "ANNEXURE I: BRSR CORE METRICS")
    rows = [
        [1, "Green-house gas (GHG) footprint", "Total Scope 1 emissions", "MT CO2e", _number(state.get("scope1", 0), 4), "Principle 6, Essential Indicators, Q7"],
        [1, "Green-house gas (GHG) footprint", "Total Scope 2 emissions", "MT CO2e", _number(state.get("scope2", 0), 4), "Principle 6, Essential Indicators, Q7"],
        [1, "Green-house gas (GHG) footprint", "GHG emission intensity (Scope 1 + 2 / revenue)", "MT CO2e / INR", _number(ghg["ghg_intensity_inr"], 8), "Principle 6, Essential Indicators, Q7"],
        [1, "Green-house gas (GHG) footprint", "GHG emission intensity per physical output", f"MT CO2e / {state.get('physical_output_unit') or 'Unit'}", _number(computed["ghg_intensity_output"], 8), "Principle 6, Essential Indicators, Q7"],
        [2, "Water footprint", "Total water consumption (withdrawal less discharge)", "KL", _number(water["water_consumption"], 2), "Principle 6, Essential Indicators, Q3"],
        [2, "Water footprint", "Water consumption intensity", "KL / INR", _number(water["water_intensity_inr"], 8), "Principle 6, Essential Indicators, Q3"],
        [2, "Water footprint", "Water consumption intensity per physical output", f"KL / {state.get('physical_output_unit') or 'Unit'}", _number(computed["water_intensity_output"], 8), "Principle 6, Essential Indicators, Q3"],
        [2, "Water footprint", "Water discharged", "KL", _number(state.get("output_m", 0), 2), "Principle 6, Essential Indicators, Q4"],
        [2, "Water footprint", "Untreated water discharged", "KL", _number(computed["water_discharge"]["untreated"], 2), "Principle 6, Essential Indicators, Q4"],
        [2, "Water footprint", "Primary treatment discharge", "KL", _number(computed["water_discharge"]["primary"], 2), "Principle 6, Essential Indicators, Q4"],
        [2, "Water footprint", "Secondary treatment discharge", "KL", _number(computed["water_discharge"]["secondary"], 2), "Principle 6, Essential Indicators, Q4"],
        [2, "Water footprint", "Tertiary treatment discharge", "KL", _number(computed["water_discharge"]["tertiary"], 2), "Principle 6, Essential Indicators, Q4"],
        [3, "Energy footprint", "Total energy consumed", "Joules / reported unit", _number(energy["total_energy_consumed"], 2), "Principle 6, Essential Indicators, Q1"],
        [3, "Energy footprint", "Energy consumed from renewable sources", "%", _number(energy["renewable_energy_share"], 2), "Principle 6, Essential Indicators, Q1"],
        [3, "Energy footprint", "Energy intensity per revenue", "Joules / INR", _number(energy["energy_intensity_inr"], 8), "Principle 6, Essential Indicators, Q1"],
        [3, "Energy footprint", "Energy intensity per physical output", f"Joules / {state.get('physical_output_unit') or 'Unit'}", _number(computed["energy_intensity_output"], 8), "Principle 6, Essential Indicators, Q1"],
    ]
    _table(pdf, headers, rows, table_widths)

    labels = (("Plastic waste", "waste_plastic"), ("E-waste", "waste_e"), ("Bio-medical waste", "waste_bio"), ("Construction and demolition waste", "waste_cd"), ("Battery waste", "waste_battery"), ("Radioactive waste", "waste_radio"), ("Other hazardous waste", "waste_haz"), ("Other non-hazardous waste", "waste_nonhaz"))
    waste_rows = [[4, "Circularity and waste management", label, "MT", _number(state.get(key, 0), 4), "Principle 6, Essential Indicators, Q9"] for label, key in labels]
    waste_rows += [[4, "Circularity and waste management", "Total waste generated", "MT", _number(waste["total_waste_generated"], 4), "Principle 6, Essential Indicators, Q9"], [4, "Circularity and waste management", "Waste recovered / recycled", "MT", _number(state.get("waste_recovered", 0), 4), "Principle 6, Essential Indicators, Q9"], [4, "Circularity and waste management", "Waste recovery rate", "%", _number(waste["waste_recovery_percentage"], 2), "Principle 6, Essential Indicators, Q9"]]
    waste_rows += [
        [4, "Circularity and waste management", "Waste intensity per revenue", "MT / INR", _number(waste["waste_intensity_inr"], 8), "Principle 6, Essential Indicators, Q9"],
        [4, "Circularity and waste management", "Waste intensity per physical output", f"MT / {state.get('physical_output_unit') or 'Unit'}", _number(computed["waste_intensity_output"], 8), "Principle 6, Essential Indicators, Q9"],
        [4, "Circularity and waste management", "Waste disposed through incineration", "MT", _number(computed["waste_disposal"]["incinerated"], 4), "Principle 6, Essential Indicators, Q9"],
        [4, "Circularity and waste management", "Waste sent to landfill", "MT", _number(computed["waste_disposal"]["landfilled"], 4), "Principle 6, Essential Indicators, Q9"],
        [4, "Circularity and waste management", "Waste disposed by other methods", "MT", _number(computed["waste_disposal"]["other"], 4), "Principle 6, Essential Indicators, Q9"],
    ]
    pdf.add_page()
    _section_title(pdf, "ANNEXURE I: BRSR CORE METRICS (continued)")
    _table(pdf, headers, waste_rows, table_widths)

    rows = [
        [5, "Employee wellbeing and safety", "Spending on wellbeing measures as a share of revenue", "%", _number((float(state.get("wellbeing_spend", 0) or 0) / denominator) * 100, 2), "Principle 3, Essential Indicators, Q1(c)"],
        [5, "Employee wellbeing and safety", "Lost Time Injury Frequency Rate", "Per 1 million person-hours", _number(ltifr, 4), "Principle 3, Essential Indicators, Q11"],
        [5, "Employee wellbeing and safety", "Permanent disabilities", "Number", _number(computed["permanent_disabilities"], 0), "Principle 3, Essential Indicators, Q11"],
        [5, "Employee wellbeing and safety", "Fatalities", "Number", _number(computed["fatalities"], 0), "Principle 3, Essential Indicators, Q11"],
        [6, "Gender diversity", "Gross wages paid to females as a share of total wages", "%", _number(gender, 2), "Principle 5, Essential Indicators, Q3(b)"],
        [6, "Gender diversity", "POSH complaints reported", "Number", _number(state.get("posh_reported", 0), 0), "Principle 5, Essential Indicators, Q7"],
        [6, "Gender diversity", "POSH complaints upheld", "Number", _number(state.get("posh_upheld", 0), 0), "Principle 5, Essential Indicators, Q7"],
        [6, "Gender diversity", "POSH complaints as % of female workforce", "%", _number(computed["posh_complaint_percentage"], 4), "Principle 5, Essential Indicators, Q7"],
        [7, "Inclusive development", "Procurement sourced from MSMEs / small producers", "%", _number(inclusive["msme_procurement_percentage"], 2), "Principle 8, Essential Indicators, Q4"],
        [7, "Inclusive development", "Wages paid in smaller towns", "%", _number(inclusive["rural_job_creation_ratio"] + inclusive["semi_urban_job_creation_ratio"], 2), "Principle 8, Essential Indicators, Q5"],
        [8, "Fairness with customers and suppliers", "Instances involving loss / breach of customer data", "% of cyber events", _number(computed["data_breach_percentage"], 4), "Principle 9, Essential Indicators, Q7"],
        [8, "Fairness with customers and suppliers", "Number of days of accounts payable", "Days", _number(ap_days, 2), "Principle 1, Essential Indicators, Q8"],
        [9, "Open-ness of business", "Share of related-party purchases", "%", _number(rpt["rpt_purchase_percentage"], 2), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Share of related-party sales", "%", _number(rpt["rpt_sales_percentage"], 2), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Purchases from trading houses", "% of total purchases", _number(computed["trading_house_purchase_percentage"], 4), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Top 10 trading-house purchases", "% of trading-house purchases", _number(computed["top_10_trading_house_percentage"], 4), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Number of trading houses", "Number", _number(state.get("trading_house_count", 0), 0), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Sales to dealers / distributors", "% of total sales", _number(computed["dealer_sales_percentage"], 4), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Top 10 dealer / distributor sales", "% of dealer sales", _number(computed["top_10_dealer_sales_percentage"], 4), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Number of dealers / distributors", "Number", _number(state.get("dealer_distributor_count", 0), 0), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Share of related-party loans & advances", "%", _number(rpt["rpt_loan_percentage"], 4), "Principle 1, Essential Indicators, Q9"],
        [9, "Open-ness of business", "Share of related-party investments", "%", _number(rpt["rpt_investment_percentage"], 4), "Principle 1, Essential Indicators, Q9"],
    ]
    pdf.add_page()
    _section_title(pdf, "ANNEXURE I: BRSR CORE METRICS (continued)")
    _table(pdf, headers, rows, table_widths)
    pdf.ln(7)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, "PRE-ASSURANCE OBSERVATIONS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=8.5)
    pdf.multi_cell(0, 5, state.get("assurance_observations") or "No observations recorded.")
    pdf.ln(3)
    pdf.multi_cell(0, 5, "Important: This generated document is an Annexure I-aligned working report based on the supplied SEBI formats. The reporting entity remains responsible for completing all mandatory BRSR disclosures, units, evidence, and assurance requirements before submission.")
    return bytes(pdf.output())
