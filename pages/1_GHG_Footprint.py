import streamlit as st
import datetime
from utils.ui_components import format_intensity, render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calc_intensity, calculate_ghg_intensity
from utils.storage import persistent_widget, save_company_state

setup_page("GHG Footprint")

# 1. Retrieve Baseline Financials
revenue_baseline = st.session_state.get("revenue", 0.0)

render_section_header("ENVIRONMENTAL PILLAR: GHG FOOTPRINT", "Scope 1 and Scope 2 emissions reporting.")

# UI Warning if Revenue is missing (Required for Intensity)
if revenue_baseline <= 0:
    st.markdown(
        """<div style='padding:15px; border:1px solid #D7191C; color:#D7191C; background-color:#FFF5F5; margin-bottom:20px;'>
        <strong>DATA WARNING:</strong> Total Turnover in Section A is 0. Intensity metrics will not be accurate until Turnover is entered.
        </div>""", unsafe_allow_html=True
    )

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Emission Inputs (MT CO2e)")
    # Using 'key' to bind to state
    persistent_widget(st.number_input, "Total Scope 1 Emissions", "scope1", format="%.4f")
    persistent_widget(st.number_input, "Total Scope 2 Emissions", "scope2", format="%.4f")
    
    if st.button("Save GHG Footprint", type="primary"):
        save_company_state()
        st.toast("GHG metrics persisted to storage.")

with col2:
    st.markdown("### Performance Metrics")
    
    # 2. Perform Calculation
    # Note: PPP is set to 1.0 default if not defined in Section A
    metrics = calculate_ghg_intensity(
        st.session_state.scope1, 
        st.session_state.scope2, 
        revenue_baseline, 
        1.0
    )
    
    # 3. Display Absolute Metric
    st.metric("Total Absolute Emissions", f"{metrics['absolute_emissions']} MT CO2e")
    
    # 4. Display Intensity Metric (The part that was missing)
    st.metric(
        label="GHG Intensity (MT / INR Turnover)", 
        value=f"{metrics['ghg_intensity_inr']}",
        help="Calculated as (Scope 1 + Scope 2) / Total Turnover"
    )
    
    st.metric(
        label="GHG Intensity (PPP Adjusted)", 
        value=f"{metrics['ghg_intensity_ppp']}"
    )
    st.metric(
        label="GHG Intensity per Physical Output",
        value=format_intensity(calc_intensity(metrics["absolute_emissions"], st.session_state.get("physical_output_quantity", 0)), f"MT CO2e/{st.session_state.get('physical_output_unit', 'Unit')}")
    )

render_regulatory_footnote(6, 7)
