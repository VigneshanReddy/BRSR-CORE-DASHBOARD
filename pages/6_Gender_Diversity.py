import streamlit as st
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calculate_gender_metrics
from utils.storage import persistent_widget, save_company_state

setup_page("Gender Diversity")

render_section_header("SOCIAL PILLAR: GENDER DIVERSITY", "Wage parity and POSH reporting as per Principle 5, Essential Questions 3(b) and 7.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Compensation Data")
    persistent_widget(st.number_input, "Total Gross Wages Paid (INR)", "total_wages", format="%.2f")
    persistent_widget(st.number_input, "Gross Wages Paid to Females (INR)", "female_wages", format="%.2f")
    persistent_widget(st.number_input, "Female Workforce", "female_workforce", min_value=0.0, step=1.0)
    persistent_widget(st.number_input, "POSH Complaints Reported", "posh_reported", min_value=0, step=1)
    persistent_widget(st.number_input, "POSH Complaints Upheld", "posh_upheld", min_value=0, step=1)
    
    if st.button("Save Diversity Data", type="primary"):
        save_company_state()
        st.toast("Gender data persisted.")

with col2:
    st.markdown("### Diversity Metric")
    wage_pct = calculate_gender_metrics(st.session_state.female_wages, st.session_state.total_wages)
    st.metric("Female Wage Share (%)", f"{wage_pct}%")
    posh_pct = (st.session_state.posh_reported / st.session_state.female_workforce * 100) if st.session_state.female_workforce else 0.0
    st.metric("POSH Complaints (% of Female Workforce)", f"{posh_pct:.4f}%")

render_regulatory_footnote(5, "3(b) & 7")
