import streamlit as st
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calculate_inclusive_dev
from utils.storage import persistent_widget, save_company_state

setup_page("Inclusive Development")

render_section_header("SOCIAL PILLAR: INCLUSIVE DEVELOPMENT", "MSME and Geographic wage tracking as per Principle 8, Essential Q4 & 5.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Procurement")
    persistent_widget(st.number_input, "Total Procurement Value (INR)", "total_proc", format="%.2f")
    persistent_widget(st.number_input, "Procurement from MSMEs (INR)", "msme_proc", format="%.2f")
    
    st.markdown("---")
    st.markdown("### Small Town Wages")
    # Using 'total_wages' from Page 6 or independent entry
    persistent_widget(st.number_input, "Wages Paid: Rural", "rural_wages", format="%.2f")
    persistent_widget(st.number_input, "Wages Paid: Semi-Urban", "semi_urban_wages", format="%.2f")

    if st.button("Save Inclusion Data", type="primary"):
        save_company_state()
        st.toast("Inclusive development data persisted.")

with col2:
    st.markdown("### Inclusion Performance")
    # Ensure total wages is not zero for division
    t_wages = st.session_state.get("total_wages", 1.0)
    if t_wages == 0: t_wages = 1.0
    
    metrics = calculate_inclusive_dev(
        st.session_state.msme_proc, 
        st.session_state.total_proc, 
        st.session_state.rural_wages, 
        st.session_state.semi_urban_wages, 
        t_wages
    )
    
    st.metric("MSME Procurement Share", f"{metrics['msme_procurement_percentage']}%")
    st.metric("Rural Wage Ratio", f"{metrics['rural_job_creation_ratio']}%")

render_regulatory_footnote(8, "4 & 5")
