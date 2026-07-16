import streamlit as st
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calculate_accounts_payable_days
from utils.storage import persistent_widget, save_company_state

setup_page("Customer & Supplier Fairness")

render_section_header("GOVERNANCE: FAIRNESS IN ENGAGEMENT", "Data breaches and Accounts Payable cycle as per Principle 9 & 1.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Data Privacy")
    persistent_widget(st.number_input, "Customer Data Breaches", "total_breaches", min_value=0, step=1)
    persistent_widget(st.number_input, "Total Cyber Security Events", "total_cyber_events", min_value=0.0, step=1.0)
    
    st.markdown("---")
    st.markdown("### Supplier Payments")
    persistent_widget(st.number_input, "Total Accounts Payable (INR)", "accounts_payable", format="%.2f")
    persistent_widget(st.number_input, "Cost of Goods Procured (INR)", "cost_procured", format="%.2f")

    if st.button("Save Engagement Data", type="primary"):
        save_company_state()
        st.toast("Fairness data persisted.")

with col2:
    st.markdown("### Efficiency Metric")
    ap_days = calculate_accounts_payable_days(st.session_state.accounts_payable, st.session_state.cost_procured)
    st.metric("Accounts Payable Cycle", f"{ap_days} Days")
    breach_pct = (st.session_state.total_breaches / st.session_state.total_cyber_events * 100) if st.session_state.total_cyber_events else 0.0
    st.metric("Customer Data Breaches (%)", f"{breach_pct:.4f}%")

render_regulatory_footnote(9, "7 & 1")
