import streamlit as st

from utils.ui_components import setup_page


setup_page("ESG Reporting Suite", configure_page=True, render_footer=False)

navigation = st.navigation(
    {
        "BRSR Core Reporting": [
            st.Page("pages/general_disclosures.py", title="General Disclosures", icon=":material/domain:"),
            st.Page("pages/1_GHG_Footprint.py", title="GHG Footprint", icon=":material/co2:"),
            st.Page("pages/2_Water_Footprint.py", title="Water Footprint", icon=":material/water_drop:"),
            st.Page("pages/3_Energy_Footprint.py", title="Energy Footprint", icon=":material/bolt:"),
            st.Page("pages/4_Circularity_Waste.py", title="Circularity & Waste", icon=":material/recycling:"),
            st.Page("pages/5_Employee_Wellbeing_Safety.py", title="Employee Wellbeing & Safety", icon=":material/health_and_safety:"),
            st.Page("pages/6_Gender_Diversity.py", title="Gender Diversity", icon=":material/diversity_3:"),
            st.Page("pages/7_Inclusive_Development.py", title="Inclusive Development", icon=":material/groups:"),
            st.Page("pages/8_Customer_Supplier_Fairness.py", title="Customer & Supplier Fairness", icon=":material/handshake:"),
            st.Page("pages/9_Openness_of_Business.py", title="Openness of Business", icon=":material/account_balance:"),
        ],
        "Assurance & Export": [
            st.Page("pages/10_Assurance_Readiness.py", title="Assurance Readiness", icon=":material/verified:"),
            st.Page("pages/11_Export_Report.py", title="Export Report", icon=":material/download:"),
        ],
    },
    position="sidebar",
)

navigation.run()
