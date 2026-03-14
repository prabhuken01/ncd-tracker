"""
NCD Tracker - Configuration File
Centralized configuration for file paths, constants, and settings
"""

import os
from pathlib import Path

# ===== FILE PATHS =====
# Auto-detect environment
IS_CLOUD = os.path.exists('/mount/src')  # Streamlit Cloud specific path

if IS_CLOUD:
    # Running on Streamlit Cloud
    BASE_DIR = Path(__file__).parent
    DATA_FILE = BASE_DIR / "Bond_Primary_Deals.xlsx"
    TERM_SHEET_TEMPLATE = BASE_DIR / "Term_Sheet_Template.docx"
    ISSUANCE_FOLDER = BASE_DIR / "issuances"
else:
    # Running locally — all files are now inside Code_Streamlit
    BASE_DIR = Path(__file__).parent
    DATA_FILE = BASE_DIR / "Bond_Primary_Deals.xlsx"
    TERM_SHEET_TEMPLATE = BASE_DIR / "Term_Sheet_Template.docx"
    ISSUANCE_FOLDER = BASE_DIR / "Issuance"

# Create necessary directories
try:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    ISSUANCE_FOLDER.mkdir(parents=True, exist_ok=True)
except:
    pass  # Ignore errors in cloud environment

# Sheet names in Excel file
SHEET_PIPELINE = "Issuance Pipeline"
SHEET_CLOSED = "Closed NCD Deal"

# ===== GOOGLE SHEETS =====
GOOGLE_SHEET_NAME = "Issuance Tracker"
GOOGLE_CREDS_FILE = BASE_DIR / "service_account.json"


def google_creds_available() -> bool:
    """Return True if Google credentials are available — local file OR Streamlit Secrets."""
    if GOOGLE_CREDS_FILE.exists():
        return True
    try:
        import streamlit as st
        return hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets
    except Exception:
        return False

# ===== APPLICATION SETTINGS =====
APP_TITLE = "Issuance Tracker"
APP_SUBTITLE = "Structured Product Solutions — Issuer Readiness"
PAGE_ICON = "📊"

# ===== FIELD CONFIGURATIONS =====
# Amount format
AMOUNT_UNIT = "₹ Cr"
AMOUNT_DECIMAL_PLACES = 2

# Interest/Coupon format
INTEREST_DECIMAL_PLACES = 2

# Date format
DATE_FORMAT = "%d/%m/%Y"
DATE_INPUT_FORMAT = "DD/MM/YYYY"

# ===== DROPDOWN OPTIONS =====
INSTRUMENT_TYPES = ["Listed NCD", "Unlisted NCD"]
ISSUER_TYPES     = ["FS", "EF"]          # FS = Financial Sector; EF = Enterprise Finance
ASSET_CLASSES    = ["NBFC", "Housing Finance", "MFI", "Corporate"]
RATING_OPTIONS = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-", "Unrated"]
SECURITY_TYPES = [
    "Unsecured",
    "Secured - Hypothecation (Floating charge)",
    "Secured - Mortgage (Immovable assets)",
    "Secured - Pledge",
    "Partly Secured"
]

# ===== STATUS OPTIONS =====
STATUS_OPTIONS = ["Pending", "In Progress", "Completed", "Blocked"]

# ===== T-DAY COUNTDOWN COLORS =====
T_COUNTDOWN_COLORS = {
    "critical": "#FF4444",   # Red - 7 days or less
    "warning": "#FFA500",    # Orange - 8-14 days
    "normal": "#4CAF50"      # Green - 15+ days
}

# ===== PHASE DEFINITIONS =====
PHASE_NAMES = [
    "Pre-Exec",
    "Depo & Stamp",
    "Docs & EBP",
    "T-Day",
    "Post"
]

PHASE_ICONS = {
    "Pre-Exec": "📋",
    "Depo & Stamp": "🏦",
    "Docs & EBP": "📝",
    "T-Day": "💰",
    "Post": "📤"
}

# ===== UI SETTINGS =====
CARD_WIDTH = 350
CARD_HEIGHT = 180
PROGRESS_BAR_HEIGHT = 10

# ===== VALIDATION RULES =====
MIN_ISSUANCE_SIZE = 1  # Rs Crore
MAX_ISSUANCE_SIZE = 10000  # Rs Crore
MIN_COUPON_RATE = 0.0  # %
MAX_COUPON_RATE = 25.0  # %
MIN_TENOR_MONTHS = 1
MAX_TENOR_MONTHS = 120

# ===== ERROR MESSAGES =====
ERROR_FILE_NOT_FOUND = "Excel file not found. Please check the file path in config.py"
ERROR_SHEET_NOT_FOUND = "Required sheet '{}' not found in Excel file"
ERROR_INVALID_DATA = "Invalid data format. Please check your inputs"
ERROR_DUPLICATE_ENTRY = "A deal with this company name already exists"

# ===== SUCCESS MESSAGES =====
SUCCESS_DEAL_CREATED = "✅ New deal created successfully!"
SUCCESS_DEAL_UPDATED = "✅ Deal updated successfully!"
SUCCESS_DEAL_CLOSED = "✅ Deal moved to Closed NCD Deals!"
SUCCESS_TERM_SHEET_GENERATED = "✅ Term sheet generated successfully!"

# ===== INFO TOOLTIPS =====
TOOLTIPS = {
    "company_name": "Enter the full legal name of the issuer company",
    "instrument_type": "Listed NCDs are traded on stock exchanges; Unlisted are privately placed",
    "asset_class": "Select the business category of the issuer",
    "issuance_size": f"Enter amount in {AMOUNT_UNIT} (minimum {MIN_ISSUANCE_SIZE}, maximum {MAX_ISSUANCE_SIZE})",
    "funding_date": "The target date (T-Day) when funds will be received",
    "rating": "Current credit rating from recognized agencies, or select Unrated",
    "security": "Type of collateral backing the NCDs",
    "coupon_rate": f"Annual interest rate in % with {INTEREST_DECIMAL_PLACES} decimals",
    "tenor": "Duration in months from issuance to maturity"
}
