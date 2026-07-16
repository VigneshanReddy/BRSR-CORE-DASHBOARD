# utils/validators.py
import re
import streamlit as st


def validate_cin(cin):
    """Return True only for a valid 21-character Indian CIN."""
    normalized_cin = re.sub(r"[\s-]+", "", cin or "").upper()
    return bool(re.fullmatch(
        r"^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$",
        normalized_cin,
    ))

def validate_positive_metric(value, label):
    """
    Verifies that quantitative metrics are non-negative.
    """
    if value < 0:
        st.markdown(
            f"""
            <div style="border: 1px solid #D7191C; background-color: #FFF5F5; padding: 10px; color: #D7191C; font-size: 0.85rem; border-radius: 0px !important;">
                <strong>DATA INTEGRITY ERROR:</strong> {label} cannot be negative.
            </div>
            """,
            unsafe_allow_html=True
        )
        return False
    return True

def validate_percentage_range(value, label):
    """
    Verifies that percentage values sit within the logical [0, 100] interval.
    """
    if not (0 <= value <= 100):
        st.markdown(
            f"""
            <div style="border: 1px solid #D7191C; background-color: #FFF5F5; padding: 10px; color: #D7191C; font-size: 0.85rem; border-radius: 0px !important;">
                <strong>LOGICAL VALIDATION ERROR:</strong> {label} must be between 0 and 100 percent.
            </div>
            """,
            unsafe_allow_html=True
        )
        return False
    return True
