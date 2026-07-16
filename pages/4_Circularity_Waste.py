import streamlit as st
from utils.ui_components import format_intensity, render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calc_intensity, calculate_waste_metrics
from utils.storage import persistent_widget, save_company_state

setup_page("Circularity & Waste")

# Retrieve baseline financial data
turnover = st.session_state.get("revenue", 1.0)
if turnover == 0: turnover = 1.0 

render_section_header("ENVIRONMENTAL PILLAR: CIRCULARITY & WASTE", "Waste management as per Principle 6, Essential Question 9.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Waste Generation (Metric Tonnes)")
    # Bound to flat session state keys defined in storage.py
    persistent_widget(st.number_input, "Plastic Waste", "waste_plastic", format="%.4f")
    persistent_widget(st.number_input, "E-waste", "waste_e", format="%.4f")
    persistent_widget(st.number_input, "Bio-medical Waste", "waste_bio", format="%.4f")
    persistent_widget(st.number_input, "Construction & Demolition Waste", "waste_cd", format="%.4f")
    persistent_widget(st.number_input, "Battery Waste", "waste_battery", format="%.4f")
    persistent_widget(st.number_input, "Radioactive Waste", "waste_radio", format="%.4f")
    persistent_widget(st.number_input, "Hazardous Waste", "waste_haz", format="%.4f")
    persistent_widget(st.number_input, "Non-hazardous Waste", "waste_nonhaz", format="%.4f")
    
    st.markdown("---")
    persistent_widget(st.number_input, "Total Waste Recovered/Recycled", "waste_recovered", format="%.4f")
    st.markdown("#### Waste Disposal by Method (MT)")
    persistent_widget(st.number_input, "Waste Incinerated", "waste_incinerated", min_value=0.0, format="%.4f")
    persistent_widget(st.number_input, "Waste Sent to Landfill", "waste_landfilled", min_value=0.0, format="%.4f")
    persistent_widget(st.number_input, "Waste Disposed by Other Methods", "waste_other_disposal", min_value=0.0, format="%.4f")
    
    if st.button("Save Waste Metrics", type="primary"):
        save_company_state()
        st.toast("Waste data persisted.")

with col2:
    st.markdown("### Performance Metrics")
    
    # Collect all 8 categories into the list for calculation
    waste_list = [
        st.session_state.waste_plastic, st.session_state.waste_e,
        st.session_state.waste_bio, st.session_state.waste_cd,
        st.session_state.waste_battery, st.session_state.waste_radio,
        st.session_state.waste_haz, st.session_state.waste_nonhaz
    ]
    
    # CORRECTED CALL: Passing 4 arguments (waste_list, recovered, turnover, ppp=1.0)
    metrics = calculate_waste_metrics(
        waste_list, 
        st.session_state.waste_recovered, 
        turnover, 
        1.0
    )
    
    c1, c2 = st.columns(2)
    c1.metric("Total Waste Generated", f"{metrics['total_waste_generated']} MT")
    c2.metric("Recovery Rate (%)", f"{metrics['waste_recovery_percentage']}%")
    
    st.markdown("---")
    st.metric("Waste Intensity (MT/INR)", format_intensity(metrics["waste_intensity_inr"], "MT/INR"))
    st.metric("Waste Intensity (PPP Adjusted)", metrics["waste_intensity_ppp"])
    st.metric("Waste Intensity per Physical Output", format_intensity(calc_intensity(metrics["total_waste_generated"], st.session_state.get("physical_output_quantity", 0)), f"MT/{st.session_state.get('physical_output_unit', 'Unit')}"))

render_regulatory_footnote(6, 9)
