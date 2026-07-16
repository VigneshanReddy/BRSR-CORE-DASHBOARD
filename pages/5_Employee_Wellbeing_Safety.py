import streamlit as st
import datetime
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calculate_ltifr
from utils.storage import persistent_widget, save_company_state

setup_page("Employee Wellbeing & Safety")

# Corrected flat state access
revenue = st.session_state.get("revenue", 0.0)
if revenue == 0: revenue = 1.0 

render_section_header("SOCIAL PILLAR: EMPLOYEE WELLBEING & SAFETY", "Reporting as per Principle 3, Essential Questions 1(c) and 11.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Wellbeing Expenditure")
    persistent_widget(st.number_input, "Total Spending on Wellbeing Measures (INR)", "wellbeing_spend", format="%.2f")
    
    st.markdown("---")
    st.markdown("### Safety Incidents")
    persistent_widget(st.number_input, "Total Person-Hours Worked", "working_hours", format="%.0f")
    persistent_widget(st.number_input, "Total Lost Time Injuries (LTI)", "lti_count", step=1.0)
    persistent_widget(st.number_input, "Permanent Disabilities", "permanent_disabilities", min_value=0.0, step=1.0)
    persistent_widget(st.number_input, "Fatalities", "fatalities", min_value=0.0, step=1.0)
    
    if st.button("Save Wellbeing Data", type="primary"):
        save_company_state()
        st.toast("Safety data persisted.")

with col2:
    st.markdown("### Performance Indices")
    ltifr = calculate_ltifr(st.session_state.lti_count, st.session_state.working_hours)
    wellbeing_pct = (st.session_state.wellbeing_spend / revenue * 100)
    
    st.metric("LTIFR (Per 1M Hours)", ltifr)
    st.metric("Wellbeing Spend %", f"{round(wellbeing_pct, 4)}%")
    st.metric("Permanent Disabilities", st.session_state.permanent_disabilities)
    st.metric("Fatalities", st.session_state.fatalities)

render_regulatory_footnote(3, "1(c) & 11")
