import streamlit as st
import datetime
from utils.ui_components import format_intensity, render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calc_intensity, calculate_water_metrics
from utils.storage import persistent_widget, save_company_state

setup_page("Water Footprint")

# Corrected flat state retrieval
turnover = st.session_state.get("revenue", 1.0)
if turnover == 0: turnover = 1.0 # Prevent zero division in display

render_section_header("ENVIRONMENTAL PILLAR: WATER FOOTPRINT", "Monitoring of water withdrawal and consumption as per Principle 6, Essential Questions 3 & 4.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Withdrawal Meters (Kilolitres)")
    # Using 'key' to bind directly to the flat session state
    persistent_widget(st.number_input, "Total Water Withdrawal (Input)", "input_m", format="%.2f")
    persistent_widget(st.number_input, "Total Water Discharged (Output)", "output_m", format="%.2f")
    st.markdown("#### Discharge by Treatment Level (KL)")
    persistent_widget(st.number_input, "Untreated Water Discharged", "water_untreated", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Primary Treatment Discharge", "water_primary_treated", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Secondary Treatment Discharge", "water_secondary_treated", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Tertiary Treatment Discharge", "water_tertiary_treated", min_value=0.0, format="%.2f")
    
    st.markdown("---")
    if st.button("Save Water Metrics", type="primary"):
        save_company_state()
        st.toast("Water data persisted.")

with col2:
    st.markdown("### Consumption Analysis")
    # Pull values directly from state for calculation
    metrics = calculate_water_metrics(
        st.session_state.input_m, 
        st.session_state.output_m, 
        turnover, 
        1.0
    )
    
    st.metric("Net Consumption", f"{metrics['water_consumption']} KL")
    st.metric("Water Intensity (KL/INR)", format_intensity(metrics["water_intensity_inr"], "KL/INR"))
    st.metric("Water Intensity per Physical Output", format_intensity(calc_intensity(metrics["water_consumption"], st.session_state.get("physical_output_quantity", 0)), f"KL/{st.session_state.get('physical_output_unit', 'Unit')}"))

render_regulatory_footnote(6, "3 & 4")
