import re

import streamlit as st

from utils.storage import init_app_state


NAVY = "#0B2E59"


def format_intensity(val, unit):
    """Keep small but meaningful intensity values visible in the UI."""
    if val is None:
        return "N/A"
    if val != 0 and abs(val) < 0.01:
        return f"{val:.4g} {unit}"
    return f"{val:.4f} {unit}"


def inject_corporate_css():
    """Apply the shared investor-ready visual system to every app page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
            color: #172033;
        }
        .stApp { background: #FFFFFF; }
        .block-container { max-width: 1440px; padding-top: 2.5rem; padding-bottom: 3rem; }

        [data-testid="stSidebar"] {
            background: #F6F8FB;
            border-right: 1px solid #E2E8F0;
        }
        
        /* Removed the restrictive flex-box rules to allow natural layout */
        [data-testid="stSidebar"] > div:first-child { padding-top: 0; }
        
        /* Inject the safely URL-encoded SVG above the navigation links */
        [data-testid="stSidebarNav"] {
            padding-top: 110px !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='86' viewBox='0 0 420 86'%3E%3Crect width='420' height='86' rx='10' fill='%23F6F8FB'/%3E%3Crect x='0' y='0' width='7' height='86' fill='%230B2E59'/%3E%3Ctext x='25' y='34' font-family='Arial, sans-serif' font-size='14' font-weight='700' fill='%2359708E'%3ESEBI BRSR CORE%3C/text%3E%3Ctext x='25' y='62' font-family='Arial, sans-serif' font-size='25' font-weight='700' fill='%230B2E59'%3EESG Reporting Suite%3C/text%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: top center;
            background-size: 95%;
            margin-top: 0.5rem;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 8px;
            color: #405069;
            font-weight: 500;
            margin: 0.1rem 0.75rem;
            padding: 0.45rem 0.65rem;
        }
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: #E8F0F9;
            color: #0B2E59;
        }

        .section-heading { margin: 0 0 0.35rem; color: #0B2E59; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.035em; }
        .section-description { margin: 0 0 1.8rem; color: #62738B; font-size: 0.95rem; line-height: 1.6; }
        .card-heading { color: #0B2E59; font-size: 1rem; font-weight: 700; margin: 0 0 1.1rem; }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF;
            border: 1px solid #E1E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 3px 12px rgba(15, 43, 77, 0.05);
            padding: 0.35rem 0.4rem;
        }
        [data-testid="stMetric"] {
            background: #F8FAFC;
            border: 1px solid #E5EAF0;
            border-radius: 10px;
            padding: 0.9rem 1rem;
        }
        [data-testid="stMetricValue"] { color: #0B2E59; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: #64748B; font-size: 0.82rem; }

        .stButton > button, [data-testid="stDownloadButton"] > button {
            background: #0B2E59 !important;
            border: 1px solid #0B2E59 !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            font-weight: 600;
            padding: 0.55rem 1.15rem;
            transition: background 0.15s ease, transform 0.15s ease;
        }
        .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
            background: #174A80 !important;
            border-color: #174A80 !important;
            transform: translateY(-1px);
        }
        [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
        [data-testid="stSelectbox"] > div > div, [data-testid="stTextArea"] textarea {
            border-color: #CBD5E1 !important;
            border-radius: 8px !important;
        }
        [data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus { border-color: #174A80 !important; box-shadow: 0 0 0 2px #DCEAF8 !important; }

        .regulatory-footnote { margin-top: 2.5rem; padding: 1rem 1.15rem; border: 1px solid #E1E8F0; border-radius: 10px; background: #F8FAFC; color: #526174; font-size: 0.82rem; line-height: 1.55; }
        .sidebar-footer { margin-top: auto; padding: 1rem 0.75rem 0.45rem; border-top: 1px solid #DCE4EE; color: #526174; font-size: 0.78rem; line-height: 1.5; }
        .sidebar-footer__name { color: #0B2E59; font-weight: 700; }
        .sidebar-footer a { color: #174A80; font-weight: 600; text-decoration: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_footer():
    """Render attribution and project context at the bottom of the sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-footer__name">Vigneshan V</div>
                <div>MBA Forestry Management</div>
                <div>IIFM Bhopal</div>
                <div style="margin-top: 0.45rem;">
                    <a href="https://www.linkedin.com/in/vigneshan-v-2503a7277?lipi=urn%3Ali%3Apage%3Ad_flagship3_messaging_conversation_detail%3B0DgG6ZJ%2BQDWCWgqFS%2FyCmA%3D%3D" target="_blank">LinkedIn</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("About this project"):
            st.markdown(
                """
                **Why I built this**

                This app supports the SEBI BRSR Core mandate (Circular
                SEBI/HO/CFD/CFD-SEC-2/P/CIR/2023/122), helping listed entities
                replace manual spreadsheet compilation with structured,
                assurance-ready ESG disclosure across nine attributes.

                **How it's built**

                A Streamlit multi-page application uses centralized session
                persistence, a validated calculation engine that separates raw
                inputs from derived KPIs, and a PDF export aligned to the SEBI
                Annexure I format.

                **Domain grounding**

                Metric definitions follow Annexure I methodology and its
                Principle/Question references, including GHG intensity
                (Principle 6, Q7) and LTIFR (Principle 3, Q11).
                """
            )

def setup_page(page_title, configure_page=False, render_footer=True):
    """Apply shared configuration, theme, state initialization, and footer."""
    if configure_page:
        st.set_page_config(
            page_title=page_title,
            page_icon="ESG",
            layout="wide",
            initial_sidebar_state="expanded",
        )
    inject_corporate_css()
    init_app_state()
    if render_footer:
        render_sidebar_footer()


def render_regulatory_footnote(principle_num, question_num):
    st.markdown(
        f"""
        <div class="regulatory-footnote">
            <strong>Regulatory provenance</strong><br>
            This data segment is mapped to SEBI BRSR Core Principle {principle_num}, Essential Question {question_num}.
            Input metrics remain subject to the entity's evidence, review, and assurance procedures.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _title_case(title):
    acronyms = {"BRSR", "ESG", "GHG", "SEBI", "POSH", "MSME", "RPT", "PPP", "INR", "MT", "KL", "LTIFR", "FY", "Q"}
    tokens = re.split(r"(\s+|[:/&-])", title.strip())
    return "".join(token if token.upper() in acronyms or not token.isalpha() else token.capitalize() for token in tokens)


def render_section_header(title, description):
    """Render consistent, Title Case page headings and supporting copy."""
    st.markdown(
        f"<h1 class='section-heading'>{_title_case(title)}</h1><p class='section-description'>{description}</p>",
        unsafe_allow_html=True,
    )
