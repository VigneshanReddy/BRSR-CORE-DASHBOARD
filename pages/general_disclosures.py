import streamlit as st

from utils.storage import persistent_widget, save_company_state
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.validators import validate_positive_metric


setup_page("General Disclosures")


def main():
    render_section_header(
        "Section A: General Disclosures",
        "Mandatory entity and financial details that power intensity metrics across the BRSR Core reporting modules.",
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.markdown("<div class='card-heading'>Entity Identification</div>", unsafe_allow_html=True)
            persistent_widget(st.text_input, "Corporate Identity Number (CIN)", "cin", help="21-digit alphanumeric identifier assigned by the ROC.")
            persistent_widget(st.text_input, "Name of the Listed Entity", "entity_name")
            persistent_widget(st.number_input, "Year of Incorporation", "inc_year", min_value=1800, max_value=2024, step=1)
            persistent_widget(
                st.selectbox,
                "Financial Year",
                "financial_year",
                options=["FY 2023-24", "FY 2024-25", "FY 2025-26", "FY 2026-27"],
            )

    with col2:
        with st.container(border=True):
            st.markdown("<div class='card-heading'>Financial Baseline</div>", unsafe_allow_html=True)
            persistent_widget(st.selectbox, "Reporting Boundary", state_key="boundary", options=["Standalone", "Consolidated"], help="Standalone: entity only. Consolidated: entity and subsidiaries.")
            persistent_widget(st.number_input, "Total Turnover / Revenue (in INR)", "revenue", min_value=0.0, format="%.2f", help="Used as the denominator for GHG, water, energy, and waste intensity metrics.")
            persistent_widget(st.number_input, "Paid-up Capital (in INR)", "paid_up_capital", min_value=0.0, format="%.2f")
            persistent_widget(st.number_input, "Physical Output Quantity", "physical_output_quantity", min_value=0.0, format="%.4f", help="The reporting-period output used for output-based intensity metrics.")
            persistent_widget(st.text_input, "Physical Output Unit", "physical_output_unit", help="For example: MT produced, vehicles, room-nights, or units.")

    st.markdown("<div style='height: 0.7rem'></div>", unsafe_allow_html=True)
    if st.button("Save Disclosures", type="primary"):
        if validate_positive_metric(st.session_state.revenue, "Total Turnover"):
            save_company_state()
            st.toast("Disclosures saved successfully.")
        else:
            st.error("Please ensure all financial metrics are non-negative.")

    render_regulatory_footnote("General Disclosures", "Statutory Framework")


main()
