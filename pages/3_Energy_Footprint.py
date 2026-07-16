import streamlit as st
from utils.ui_components import format_intensity, render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calc_intensity, calculate_energy_metrics
from utils.storage import persistent_widget, save_company_state

setup_page("Energy Footprint")

turnover = st.session_state.get("revenue", 1.0)
if turnover == 0: turnover = 1.0

render_section_header("ENVIRONMENTAL PILLAR: ENERGY FOOTPRINT", "Energy consumption mix as per Principle 6, Essential Question 1.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Consumption by Source (Joules)")
    persistent_widget(st.number_input, "Renewable Source Consumption", "renewable", format="%.2f")
    persistent_widget(st.number_input, "Non-Renewable Source Consumption", "non_renewable", format="%.2f")
    
    if st.button("Save Energy Metrics", type="primary"):
        save_company_state()
        st.toast("Energy data persisted.")

with col2:
    st.markdown("### Energy Mix Performance")
    metrics = calculate_energy_metrics(
        st.session_state.renewable, 
        st.session_state.non_renewable, 
        turnover, 
        1.0
    )
    
    c1, c2 = st.columns(2)
    c1.metric("Total Consumption", f"{metrics['total_energy_consumed']} J")
    c2.metric("Renewable Share (%)", f"{metrics['renewable_energy_share']}%")
    st.metric("Energy Intensity (J/INR)", format_intensity(metrics["energy_intensity_inr"], "J/INR"))
    st.metric("Energy Intensity per Physical Output", format_intensity(calc_intensity(metrics["total_energy_consumed"], st.session_state.get("physical_output_quantity", 0)), f"J/{st.session_state.get('physical_output_unit', 'Unit')}"))

render_regulatory_footnote(6, 1)
