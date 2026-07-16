import streamlit as st
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.calculations import calculate_rpt_shares
from utils.storage import persistent_widget, save_company_state

setup_page("Openness of Business")

render_section_header("GOVERNANCE: OPENNESS OF BUSINESS", "Related Party Transactions (RPT) as per Principle 1, Q9.")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### RPT Tracking")
    persistent_widget(st.number_input, "RPT Purchases (INR)", "rpt_pur", format="%.2f")
    persistent_widget(st.number_input, "Total Purchases (INR)", "tot_pur", format="%.2f")
    
    persistent_widget(st.number_input, "RPT Sales (INR)", "rpt_sal", format="%.2f")
    persistent_widget(st.number_input, "Total Sales (INR)", "tot_sal", format="%.2f")
    st.markdown("#### Trading Houses and Dealers")
    persistent_widget(st.number_input, "Purchases from Trading Houses (INR)", "trading_house_purchases", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Number of Trading Houses", "trading_house_count", min_value=0, step=1)
    persistent_widget(st.number_input, "Purchases from Top 10 Trading Houses (INR)", "top_10_trading_house_purchases", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Sales to Dealers / Distributors (INR)", "dealer_distributor_sales", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Number of Dealers / Distributors", "dealer_distributor_count", min_value=0, step=1)
    persistent_widget(st.number_input, "Sales to Top 10 Dealers / Distributors (INR)", "top_10_dealer_distributor_sales", min_value=0.0, format="%.2f")
    st.markdown("#### Related-party Loans and Investments")
    persistent_widget(st.number_input, "Related-party Loans & Advances (INR)", "rpt_loans", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Total Loans & Advances (INR)", "total_loans", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Related-party Investments (INR)", "rpt_investments", min_value=0.0, format="%.2f")
    persistent_widget(st.number_input, "Total Investments (INR)", "total_investments", min_value=0.0, format="%.2f")

    concentration_errors = []
    if st.session_state.top_10_trading_house_purchases > st.session_state.trading_house_purchases:
        concentration_errors.append("Purchases from Top 10 Trading Houses cannot exceed Purchases from Trading Houses.")
    if st.session_state.top_10_dealer_distributor_sales > st.session_state.dealer_distributor_sales:
        concentration_errors.append("Sales to Top 10 Dealers / Distributors cannot exceed total Sales to Dealers / Distributors.")
    if concentration_errors:
        for message in concentration_errors:
            st.error(message)

    if st.button("Save RPT Data", type="primary"):
        if concentration_errors:
            st.error("Correct the concentration values before saving.")
        else:
            save_company_state()
            st.toast("RPT data persisted.")

with col2:
    st.markdown("### Concentration Metrics")
    # Passing dummy 1.0 for loans/investments to avoid error if not entered
    rpt_metrics = calculate_rpt_shares(
        st.session_state.rpt_pur, st.session_state.tot_pur,
        st.session_state.rpt_sal, st.session_state.tot_sal,
        st.session_state.rpt_loans, st.session_state.total_loans,
        st.session_state.rpt_investments, st.session_state.total_investments
    )
    
    st.metric("RPT Purchase Share", f"{rpt_metrics['rpt_purchase_percentage']}%")
    st.metric("RPT Sales Share", f"{rpt_metrics['rpt_sales_percentage']}%")
    st.metric("RPT Loans & Advances Share", f"{rpt_metrics['rpt_loan_percentage']}%")
    st.metric("RPT Investments Share", f"{rpt_metrics['rpt_investment_percentage']}%")
    trading_pct = (st.session_state.trading_house_purchases / st.session_state.tot_pur * 100) if st.session_state.tot_pur else 0.0
    dealer_pct = (st.session_state.dealer_distributor_sales / st.session_state.tot_sal * 100) if st.session_state.tot_sal else 0.0
    st.metric("Trading-house Purchases Share", f"{trading_pct:.4f}%")
    top_trading_pct = (st.session_state.top_10_trading_house_purchases / st.session_state.trading_house_purchases * 100) if st.session_state.trading_house_purchases else 0.0
    st.metric("Top 10 Trading-house Purchases Share", f"{top_trading_pct:.4f}%")
    st.metric("Dealer / Distributor Sales Share", f"{dealer_pct:.4f}%")
    top_dealer_pct = (st.session_state.top_10_dealer_distributor_sales / st.session_state.dealer_distributor_sales * 100) if st.session_state.dealer_distributor_sales else 0.0
    st.metric("Top 10 Dealer / Distributor Sales Share", f"{top_dealer_pct:.4f}%")

render_regulatory_footnote(1, 9)
