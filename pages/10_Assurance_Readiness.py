import streamlit as st
import datetime
from utils.ui_components import render_regulatory_footnote, render_section_header, setup_page
from utils.storage import persistent_widget, save_company_state

setup_page("Assurance Readiness")

render_section_header(
    "INSTITUTIONAL PRE-ASSURANCE PORTAL", 
    "Verification of evidence benchmarks and data integrity flags for Reasonable Assurance readiness."
)

# Structural mapping of pillars to flat session_state keys
pillars = [
    {"id": "P1", "name": "GHG Footprint", "ref": "P6, Q7", "keys": ["scope1", "scope2"]},
    {"id": "P2", "name": "Water Footprint", "ref": "P6, Q3-4", "keys": ["input_m", "output_m"]},
    {"id": "P3", "name": "Energy Footprint", "ref": "P6, Q1", "keys": ["renewable", "non_renewable"]},
    {"id": "P4", "name": "Waste Management", "ref": "P6, Q9", "keys": ["waste_plastic", "waste_haz"]},
    {"id": "P5", "name": "Employee Wellbeing", "ref": "P3, Q1, Q11", "keys": ["wellbeing_spend", "working_hours", "lti_count"]},
    {"id": "P6", "name": "Gender Diversity", "ref": "P5, Q3, Q7", "keys": ["female_wages", "total_wages"]},
    {"id": "P7", "name": "Inclusive Development", "ref": "P8, Q4-5", "keys": ["msme_proc", "rural_wages"]},
    {"id": "P8", "name": "Fairness in Engagement", "ref": "P9, Q7 / P1, Q8", "keys": ["accounts_payable", "total_breaches"]},
    {"id": "P9", "name": "Openness of Business", "ref": "P1, Q9", "keys": ["rpt_pur", "rpt_sal"]}
]

st.markdown("### Readiness Checklist & Evidence Verification")

# Formal Data Grid Headers
h1, h2, h3, h4 = st.columns([1, 2, 1, 1])
h1.markdown("**PILLAR ID**")
h2.markdown("**ESG ATTRIBUTE**")
h3.markdown("**DATA STATUS**")
h4.markdown("**AUDIT FLAG**")
st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #DEE2E6;'>", unsafe_allow_html=True)

for p in pillars:
    c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
    c1.text(p["id"])
    c2.text(f"{p['name']} ({p['ref']})")
    
    # Check for presence of data in flat state (at least one non-zero entry)
    has_data = any(st.session_state.get(k, 0.0) > 0 for k in p["keys"])
    
    status_color = "#002D62" if has_data else "#D7191C"
    status_text = "DATA PRESENT" if has_data else "NO DATA"
    
    c3.markdown(f"<span style='color: {status_color}; font-weight: 700;'>{status_text}</span>", unsafe_allow_html=True)
    
    # Checkbox bound to state for manual verification persistence
    evidence_key = f"verified_{p['id']}"
    if evidence_key not in st.session_state:
        st.session_state[evidence_key] = False
    
    persistent_widget(c4.checkbox, "Verified", evidence_key)

st.markdown("---")

# Corrected block indentation for the button logic
if st.button("COMMIT AUDIT READINESS STATE"):
    save_company_state()
    st.toast("Readiness flags successfully persisted to local storage.")

st.markdown("### Auditor Remarks")
persistent_widget(
    st.text_area,
    "Pre-Assurance Observations",
    "assurance_observations",
    placeholder="Document specific status of meter logs, purchase invoices, and payroll registers required for Reasonable Assurance."
)

render_regulatory_footnote("Assurance Readiness", "Institutional Audit")
