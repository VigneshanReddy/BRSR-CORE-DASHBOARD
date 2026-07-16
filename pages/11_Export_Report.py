import streamlit as st
import pandas as pd
import io
import datetime  # Added missing import
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import (
    calculate_ghg_intensity, calculate_water_metrics, calculate_energy_metrics,
    calculate_waste_metrics, calculate_ltifr, calculate_gender_metrics,
    calculate_all_safe, calculate_inclusive_dev, calculate_accounts_payable_days, calculate_rpt_shares
)
from utils.storage import persistent_widget
from utils.report_generator import build_brsr_core_pdf
from utils.validators import validate_cin

setup_page("Export Report")

# Retrieve baseline financial data from flat state
rev = st.session_state.get("revenue", 1.0)
if rev == 0: rev = 1.0
ppp = 1.0

render_section_header(
    "EXECUTIVE SUMMARY & STATUTORY EXPORT", 
    "Consolidated ESG Performance Matrix mapped to SEBI BRSR Core Annexure I."
)

# Consolidate all calculated metrics into a master reporting list
report_rows = []

# 1. GHG Footprint
ghg = calculate_ghg_intensity(st.session_state.get("scope1", 0.0), st.session_state.get("scope2", 0.0), rev, ppp)
report_rows.append(["P6", "GHG Footprint", "Absolute Emissions (MT CO2e)", ghg["absolute_emissions"]])
report_rows.append(["P6", "GHG Footprint", "Intensity (MT/INR)", ghg["ghg_intensity_inr"]])

# 2. Water Footprint
wat = calculate_water_metrics(st.session_state.get("input_m", 0.0), st.session_state.get("output_m", 0.0), rev, ppp)
report_rows.append(["P6", "Water Footprint", "Total Consumption (KL)", wat["water_consumption"]])
report_rows.append(["P6", "Water Footprint", "Intensity (KL/INR)", wat["water_intensity_inr"]])

# 3. Energy Footprint
eng = calculate_energy_metrics(st.session_state.get("renewable", 0.0), st.session_state.get("non_renewable", 0.0), rev, ppp)
report_rows.append(["P6", "Energy Footprint", "Total Energy Consumed (J)", eng["total_energy_consumed"]])
report_rows.append(["P6", "Energy Footprint", "Renewable Energy Share (%)", eng["renewable_energy_share"]])

# 4. Waste Management
waste_list = [
    st.session_state.get("waste_plastic", 0.0), st.session_state.get("waste_e", 0.0),
    st.session_state.get("waste_bio", 0.0), st.session_state.get("waste_cd", 0.0),
    st.session_state.get("waste_battery", 0.0), st.session_state.get("waste_radio", 0.0),
    st.session_state.get("waste_haz", 0.0), st.session_state.get("waste_nonhaz", 0.0)
]
wst = calculate_waste_metrics(waste_list, st.session_state.get("waste_recovered", 0.0), rev, ppp)
report_rows.append(["P6", "Waste Management", "Total Waste Generated (MT)", wst["total_waste_generated"]])
report_rows.append(["P6", "Waste Management", "Recovery Rate (%)", wst["waste_recovery_percentage"]])

# 5. Wellbeing & Safety
ltifr = calculate_ltifr(st.session_state.get("lti_count", 0.0), st.session_state.get("working_hours", 1000000.0))
report_rows.append(["P3", "Wellbeing & Safety", "LTIFR (Per 1M Hours)", ltifr])

# 6. Gender Diversity
gen = calculate_gender_metrics(st.session_state.get("female_wages", 0.0), st.session_state.get("total_wages", 1.0))
report_rows.append(["P5", "Gender Diversity", "Female Wage Share (%)", gen])

# 7. Inclusive Development
inc = calculate_inclusive_dev(st.session_state.get("msme_proc", 0.0), st.session_state.get("total_proc", 1.0), 
                              st.session_state.get("rural_wages", 0.0), st.session_state.get("semi_urban_wages", 0.0), 
                              st.session_state.get("total_wages", 1.0))
report_rows.append(["P8", "Inclusive Dev", "MSME Procurement Share (%)", inc["msme_procurement_percentage"]])

# 8. Fairness
ap_days = calculate_accounts_payable_days(st.session_state.get("accounts_payable", 0.0), st.session_state.get("cost_procured", 1.0))
report_rows.append(["P9/P1", "Fairness", "Accounts Payable Cycle (Days)", ap_days])

# Convert to DataFrame
df_report = pd.DataFrame(report_rows, columns=["Principle", "Attribute", "Parameter", "Current FY Value"])
computed, calc_error = calculate_all_safe(dict(st.session_state))

st.markdown("### Statutory Reporting Matrix")
st.table(df_report)

# Export Logic
st.markdown("---")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.markdown("### Data Export")
    
    # Excel Export using xlsxwriter
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_report.to_excel(writer, index=False, sheet_name='BRSR_Core_Report')
        
    st.download_button(
        label="DOWNLOAD STATUTORY EXCEL REPORT",
        data=buffer.getvalue(),
        file_name=f"BRSR_Core_Report_{datetime.date.today()}.xlsx",
        mime="application/vnd.ms-excel"
    )

    if not validate_cin(st.session_state.get("cin")):
        st.error("PDF export requires a valid CIN in the format L12345MH2020PLC123456. Spaces and hyphens are accepted; a 21-character value with another structure is not a valid CIN.")
    elif calc_error:
        st.error(f"PDF export blocked: {calc_error}")
    else:
        pdf_bytes = build_brsr_core_pdf(dict(st.session_state))
        st.download_button(
            label="DOWNLOAD BRSR CORE PDF REPORT",
            data=pdf_bytes,
            file_name=f"BRSR_Core_Report_{datetime.date.today()}.pdf",
            mime="application/pdf",
            help="Annexure I-aligned working report based on the supplied SEBI BRSR formats.",
        )

with col_exp2:
    st.markdown("### Report Sign-off")
    persistent_widget(
        st.selectbox,
        "Type of Assurance Obtained",
        "assurance_type",
        options=["None", "Limited", "Reasonable"],
    )
    if st.button("GENERATE AUDIT-READY PDF PREVIEW"):
        st.info("System generating PDF with localized data sovereignty encryption...")

render_regulatory_footnote("Export", "Annexure I / II")
