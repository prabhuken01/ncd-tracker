"""
NCD Tracker - Helpers
Miscellaneous helper functions
"""

import streamlit as st
from datetime import datetime, date
import json
from pathlib import Path

def show_info_tooltip(text, tooltip):
    """
    Display text with tooltip
    
    Args:
        text (str): Label text
        tooltip (str): Tooltip text
    """
    return f"{text} ℹ️" if tooltip else text

def display_error_messages(errors):
    """
    Display list of error messages
    
    Args:
        errors (list): List of error message strings
    """
    if errors:
        for error in errors:
            st.error(f"❌ {error}")

def display_success_message(message):
    """
    Display success message
    
    Args:
        message (str): Success message
    """
    st.success(message)

def display_warning_message(message):
    """
    Display warning message
    
    Args:
        message (str): Warning message
    """
    st.warning(f"⚠️ {message}")

def display_info_message(message):
    """
    Display info message
    
    Args:
        message (str): Info message
    """
    st.info(f"ℹ️ {message}")

def safe_division(numerator, denominator, default=0):
    """
    Safe division that returns default on division by zero
    
    Args:
        numerator (float): Numerator
        denominator (float): Denominator
        default: Default value if denominator is 0
    
    Returns:
        float: Result of division or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default

def parse_date(date_str, format_str="%d/%m/%Y"):
    """
    Parse date string to date object
    
    Args:
        date_str (str): Date string
        format_str (str): Date format
    
    Returns:
        date: Parsed date object or None
    """
    try:
        return datetime.strptime(date_str, format_str).date()
    except:
        return None

def date_to_string(date_obj, format_str="%d/%m/%Y"):
    """
    Convert date object to string
    
    Args:
        date_obj (date): Date object
        format_str (str): Date format
    
    Returns:
        str: Formatted date string
    """
    try:
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime(format_str)
    except:
        return ""

def ensure_directory_exists(path):
    """
    Create directory if it doesn't exist
    
    Args:
        path (Path or str): Directory path
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

def save_json(data, filepath):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath (str): File path
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath):
    """
    Load data from JSON file
    
    Args:
        filepath (str): File path
    
    Returns:
        dict: Loaded data or empty dict if file doesn't exist
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def create_company_folder(company_name, base_path):
    """
    Create folder for company documents
    
    Args:
        company_name (str): Company name
        base_path (Path): Base directory path
    
    Returns:
        Path: Created folder path
    """
    # Sanitize company name for folder
    safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in company_name)
    folder_path = base_path / safe_name
    ensure_directory_exists(folder_path)
    return folder_path

def init_session_state(key, default_value):
    """
    Initialize session state variable if not exists
    
    Args:
        key (str): Session state key
        default_value: Default value to set
    """
    if key not in st.session_state:
        st.session_state[key] = default_value

def get_session_state(key, default=None):
    """
    Get session state value with default
    
    Args:
        key (str): Session state key
        default: Default value if key doesn't exist
    
    Returns:
        Value from session state or default
    """
    return st.session_state.get(key, default)

def set_session_state(key, value):
    """
    Set session state value
    
    Args:
        key (str): Session state key
        value: Value to set
    """
    st.session_state[key] = value

def clear_session_state(keys=None):
    """
    Clear session state variables
    
    Args:
        keys (list): List of keys to clear, or None to clear all
    """
    if keys is None:
        st.session_state.clear()
    else:
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]

def format_checklist_json(checklists):
    """
    Format checklists dictionary to JSON for storage
    
    Args:
        checklists (dict): Dictionary of PhaseChecklist objects
    
    Returns:
        str: JSON string
    """
    data = {}
    for phase, checklist in checklists.items():
        data[phase] = checklist.to_dict()
    return json.dumps(data, default=str)

def parse_checklist_json(json_str):
    """
    Parse JSON string to checklists dictionary
    
    Args:
        json_str (str): JSON string
    
    Returns:
        dict: Dictionary of PhaseChecklist objects
    """
    from data.data_models import PhaseChecklist
    
    try:
        data = json.loads(json_str)
        checklists = {}
        for phase, checklist_data in data.items():
            checklists[phase] = PhaseChecklist.from_dict(checklist_data)
        return checklists
    except:
        return {}

def calculate_summary_stats(deals):
    """
    Calculate dashboard summary statistics
    
    Args:
        deals (list): List of PipelineDeal objects
    
    Returns:
        dict: Summary statistics
    """
    total = len(deals)
    fully_funded = sum(1 for deal in deals if deal.is_fully_funded())
    in_progress = total - fully_funded
    due_soon = sum(1 for deal in deals if deal.get_days_until_funding() <= 7)
    
    return {
        "total": total,
        "fully_funded": fully_funded,
        "in_progress": in_progress,
        "due_soon": due_soon
    }

def filter_deals_by_type(deals, instrument_type):
    """
    Filter deals by instrument type
    
    Args:
        deals (list): List of deals
        instrument_type (str): "All", "Listed NCD", or "Unlisted NCD"
    
    Returns:
        list: Filtered deals
    """
    if instrument_type == "All":
        return deals
    return [deal for deal in deals if deal.instrument_type == instrument_type]
