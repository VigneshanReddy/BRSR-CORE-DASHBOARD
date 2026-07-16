import json
import os
import uuid
import streamlit as st


def _copy_widget_to_state(state_key):
    """Copy a page-local widget value into the durable app state."""
    st.session_state[state_key] = st.session_state[f"_ui_{state_key}"]


def persistent_widget(widget, label, state_key, **kwargs):
    """Render a widget whose value survives Streamlit multipage navigation.

    Streamlit removes a widget's session-state key when its page is not
    rendered.  The widget therefore uses a private, page-local key while the
    user value is kept under ``state_key`` in the application state.
    """
    durable_keys = st.session_state.setdefault("_durable_keys", [])
    if state_key not in durable_keys:
        durable_keys.append(state_key)

    widget_key = f"_ui_{state_key}"
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state.get(state_key)

    return widget(
        label,
        key=widget_key,
        on_change=_copy_widget_to_state,
        args=(state_key,),
        **kwargs,
    )

def get_session_id():
    """Return an opaque identifier that lasts for this browser session."""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]


def get_storage_path():
    """
    Constructs an absolute path to the data storage file to prevent OS-level 
    PermissionErrors and path resolution issues across different environments.
    """
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    storage_dir = os.path.join(base_dir, "data", "sessions")
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    # Session files are plaintext and retained indefinitely. Add a separate
    # expiry/cleanup policy before using this storage in a long-lived deployment.
    return os.path.join(storage_dir, f"{get_session_id()}.json")

def init_app_state():
    """
    Initializes the flat global state architecture.
    Uses a 'Hydration Guard' (_hydrated) to ensure that local JSON data is only 
    loaded once per session. This prevents page navigation from overwriting 
    live user edits with stale data from the disk.
    """
    # 1. Comprehensive Schema Definition
    # Numeric values are explicitly defined as floats (0.0) to prevent widget type-mismatch.
    defaults = {
        # Section A: General Disclosures
        "cin": "",
        "entity_name": "",
        "inc_year": 2000,
        "financial_year": "FY 2025-26",
        "physical_output_quantity": 0.0,
        "physical_output_unit": "Unit",
        "boundary": "Standalone",
        "revenue": 0.0,
        "paid_up_capital": 0.0,
        "assurance_type": "None",
        "assurance_observations": "",
        
        # Pillar 1: GHG Footprint
        "scope1": 0.0,
        "scope2": 0.0,
        
        # Pillar 2: Water Footprint
        "input_m": 0.0,
        "output_m": 0.0,
        "water_untreated": 0.0,
        "water_primary_treated": 0.0,
        "water_secondary_treated": 0.0,
        "water_tertiary_treated": 0.0,
        
        # Pillar 3: Energy Footprint
        "renewable": 0.0,
        "non_renewable": 0.0,
        
        # Pillar 4: Waste Management (8 Statutory Categories)
        "waste_plastic": 0.0,
        "waste_e": 0.0,
        "waste_bio": 0.0,
        "waste_cd": 0.0,
        "waste_battery": 0.0,
        "waste_radio": 0.0,
        "waste_haz": 0.0,
        "waste_nonhaz": 0.0,
        "waste_recovered": 0.0,
        "waste_incinerated": 0.0,
        "waste_landfilled": 0.0,
        "waste_other_disposal": 0.0,
        
        # Pillar 5: Employee Wellbeing & Safety
        "wellbeing_spend": 0.0,
        "working_hours": 1000000.0,
        "lti_count": 0.0,
        "permanent_disabilities": 0.0,
        "fatalities": 0.0,
        
        # Pillar 6: Gender Diversity
        "female_wages": 0.0,
        "total_wages": 0.0,
        "posh_reported": 0,
        "posh_upheld": 0,
        "female_workforce": 0.0,
        
        # Pillar 7: Inclusive Development
        "total_proc": 0.0,
        "msme_proc": 0.0,
        "rural_wages": 0.0,
        "semi_urban_wages": 0.0,
        
        # Pillar 8: Fairness in Engagement
        "accounts_payable": 0.0,
        "cost_procured": 0.0,
        "total_breaches": 0,
        "total_cyber_events": 0.0,
        
        # Pillar 9: Openness of Business
        "rpt_pur": 0.0,
        "tot_pur": 0.0,
        "rpt_sal": 0.0,
        "tot_sal": 0.0,
        "trading_house_purchases": 0.0,
        "trading_house_count": 0,
        "top_10_trading_house_purchases": 0.0,
        "dealer_distributor_sales": 0.0,
        "dealer_distributor_count": 0,
        "top_10_dealer_distributor_sales": 0.0,
        "rpt_loans": 0.0,
        "total_loans": 0.0,
        "rpt_investments": 0.0,
        "total_investments": 0.0,
    }

    # Reassigning durable values on every page run prevents Streamlit's widget
    # cleanup from deleting them after the user navigates away from a page.
    already_hydrated = st.session_state.get("_hydrated", False)

    # 2. Load Persistent Data from Disk only once per browser session.
    saved_data = {}
    path = get_storage_path()
    if not already_hydrated and os.path.exists(path):
        try:
            with open(path, "r") as f:
                saved_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            saved_data = {}

    # 3. Synchronize Session State
    for key, default_val in defaults.items():
        if key not in st.session_state:
            raw_val = saved_data.get(key, default_val)
            
            # Type-Safe Casting for Floats
            if isinstance(default_val, float):
                try:
                    # Handle cases where empty strings might have been saved
                    if str(raw_val).strip() == "":
                        st.session_state[key] = 0.0
                    else:
                        st.session_state[key] = float(raw_val)
                except (ValueError, TypeError):
                    st.session_state[key] = 0.0
            else:
                # Handle Strings and Integers
                st.session_state[key] = raw_val
        else:
            # Mark this as application state (rather than orphaned widget
            # state), so it remains available when its page is not rendered.
            st.session_state[key] = st.session_state[key]

    # Preserve any additional persistent fields registered by a page (for
    # example, assurance checkboxes) as well.
    for key in st.session_state.get("_durable_keys", []):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]

    # 4. Set Hydration Flag
    st.session_state["_hydrated"] = True

def save_company_state():
    """
    Serializes the current flat session state into a local JSON file.
    Filters out internal Streamlit keys and state-management flags.
    """
    path = get_storage_path()
    # Export only non-internal keys to the storage file
    data_to_save = {
        k: v for k, v in st.session_state.items() 
        if not k.startswith("_") and k != "session_id"
    }
    
    try:
        with open(path, "w") as f:
            json.dump(data_to_save, f, indent=4)
        return True
    except IOError:
        st.error("Critical Storage Error: Unable to persist data to disk.")
        return False
