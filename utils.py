"""
NCD Tracker - Utils
Merged: helpers + formatters
All formatting, display helpers, and session-state utilities.
"""

import streamlit as st
from datetime import date, datetime, timedelta
from pathlib import Path
import json
import config


# ══════════════════════════════════════════════════
#  FORMATTERS
# ══════════════════════════════════════════════════

def format_amount(amount):
    if amount is None:
        return "N/A"
    return f"{config.AMOUNT_UNIT} {amount:,.{config.AMOUNT_DECIMAL_PLACES}f} Cr"


def format_percentage(value):
    if value is None:
        return "N/A"
    return f"{value:.{config.INTEREST_DECIMAL_PLACES}f}%"


def format_date(date_obj, include_day_name=False):
    if date_obj is None:
        return "N/A"
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, config.DATE_FORMAT).date()
        except Exception:
            return date_obj
    formatted = date_obj.strftime(config.DATE_FORMAT)
    if include_day_name:
        formatted = f"{date_obj.strftime('%A')}, {formatted}"
    return formatted


def format_t_countdown(funding_date):
    if funding_date is None:
        return "N/A"
    if isinstance(funding_date, str):
        try:
            funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
        except Exception:
            return "N/A"
    days = (funding_date - date.today()).days
    if days < 0:
        return f"T+{abs(days)}d"
    elif days == 0:
        return "T-Day"
    return f"T-{days}d"


def format_progress(completed, total):
    pct = round((completed / total) * 100) if total else 0
    return f"{completed}/{total} · {pct}%"


def format_tenor(months):
    if months is None:
        return "N/A"
    return f"{months} Month{'s' if months != 1 else ''}"


def format_isin(isin):
    if not isin or len(str(isin)) != 12:
        return isin or "N/A"
    return f"{isin[:3]} {isin[3:9]} {isin[9:]}"


def get_t_countdown_color(funding_date):
    if funding_date is None:
        return "normal"
    if isinstance(funding_date, str):
        try:
            funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
        except Exception:
            return "normal"
    days = (funding_date - date.today()).days
    if days <= 7:
        return "critical"
    elif days <= 21:
        return "warning"
    return "normal"


def get_status_emoji(status):
    return {"Pending": "⏳", "In Progress": "⚡", "Completed": "✅", "Blocked": "🚫"}.get(status, "")


def calculate_maturity_date(funding_date, tenor_months):
    if isinstance(funding_date, str):
        funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
    return funding_date + timedelta(days=tenor_months * 30)


# ══════════════════════════════════════════════════
#  DISPLAY HELPERS
# ══════════════════════════════════════════════════

def display_error_messages(errors):
    for e in (errors or []):
        st.error(f"❌ {e}")


def display_success_message(message):
    st.success(message)


def display_warning_message(message):
    st.warning(f"⚠️ {message}")


def display_info_message(message):
    st.info(f"ℹ️ {message}")


# ══════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════

def init_session_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value


def get_session_state(key, default=None):
    return st.session_state.get(key, default)


def set_session_state(key, value):
    st.session_state[key] = value


def clear_session_state(keys=None):
    if keys is None:
        st.session_state.clear()
    else:
        for k in keys:
            st.session_state.pop(k, None)


# ══════════════════════════════════════════════════
#  FILESYSTEM HELPERS
# ══════════════════════════════════════════════════

def ensure_directory_exists(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def create_company_folder(company_name, base_path):
    safe = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in company_name)
    folder = Path(base_path) / safe
    ensure_directory_exists(folder)
    return folder


def save_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ══════════════════════════════════════════════════
#  CHECKLIST JSON HELPERS
# ══════════════════════════════════════════════════

def format_checklist_json(checklists):
    return json.dumps({p: c.to_dict() for p, c in checklists.items()}, default=str)


def parse_checklist_json(json_str):
    from models import PhaseChecklist
    try:
        data = json.loads(json_str)
        return {p: PhaseChecklist.from_dict(cd) for p, cd in data.items()}
    except Exception:
        return {}


# ══════════════════════════════════════════════════
#  SUMMARY STATS & FILTERING
# ══════════════════════════════════════════════════

def calculate_summary_stats(deals):
    total        = len(deals)
    fully_funded = sum(1 for d in deals if d.is_fully_funded())
    in_progress  = total - fully_funded
    due_soon     = sum(1 for d in deals if d.get_days_until_funding() <= 7)
    return {"total": total, "fully_funded": fully_funded, "in_progress": in_progress, "due_soon": due_soon}


def filter_deals_by_type(deals, instrument_type):
    if instrument_type == "All":
        return deals
    return [d for d in deals if d.instrument_type == instrument_type]


# ══════════════════════════════════════════════════
#  MISC
# ══════════════════════════════════════════════════

def safe_division(numerator, denominator, default=0):
    try:
        return numerator / denominator if denominator != 0 else default
    except Exception:
        return default


def parse_date(date_str, format_str="%d/%m/%Y"):
    try:
        return datetime.strptime(date_str, format_str).date()
    except Exception:
        return None


def date_to_string(date_obj, format_str="%d/%m/%Y"):
    try:
        return date_obj if isinstance(date_obj, str) else date_obj.strftime(format_str)
    except Exception:
        return ""
