"""
NCD Tracker - Constants
Merged: field_definitions + checklist_items
All Excel column mappings, checklist data, and phase definitions
"""

import calendar
from datetime import date, datetime

# ===== EXCEL COLUMN MAPPINGS (actual Bond_Primary_Deals.xlsx columns) =====

# Pipeline Issuance sheet actual column names
PIPELINE_COL_ISSUER          = "Issuer"
PIPELINE_COL_DATE            = "Tentative Issuance Date"
PIPELINE_COL_TYPE            = "Listed/Unlisted"
PIPELINE_COL_ISSUER_TYPE     = "Type"         # FS / EF
PIPELINE_COL_QUANTUM         = "Quantum (Cr.)"
PIPELINE_COL_CREDIT          = "Credit Clearance"
PIPELINE_COL_RATING          = "Rating"       # may not exist – default "N/A"
PIPELINE_COL_SECURITY        = "Security"     # may not exist – default "Unsecured"
PIPELINE_COL_CHECKLIST       = "Checklist Data"   # JSON blob, added by app
PIPELINE_COL_CREATED         = "Created Date"
PIPELINE_COL_STATUS          = "Status"

# Closed NCD Deal sheet actual column names
CLOSED_COL_ISSUER            = "Issuer"
CLOSED_COL_ISSUE_DATE        = "Issue Date"
CLOSED_COL_ISIN              = "ISIN"
CLOSED_COL_COUPON            = "Coupon (XIRR)"
CLOSED_COL_TENOR             = "Tenor (Months)"
CLOSED_COL_MATURITY          = "Maturity Date"
CLOSED_COL_QUANTUM           = "Quantum (Cr.)"
CLOSED_COL_RATING            = "Rating"
CLOSED_COL_TYPE              = "Listed/Unlisted"
CLOSED_COL_ISSUER_TYPE       = "FS/EF"
CLOSED_COL_SECURITY          = "Security"     # may not exist – default "N/A"

# ===== WRITE HEADERS (what the app writes when creating a new Excel) =====
PIPELINE_HEADERS = [
    PIPELINE_COL_ISSUER,
    PIPELINE_COL_TYPE,
    PIPELINE_COL_ISSUER_TYPE,
    PIPELINE_COL_QUANTUM,
    PIPELINE_COL_DATE,
    PIPELINE_COL_CREDIT,
    PIPELINE_COL_RATING,
    PIPELINE_COL_SECURITY,
    PIPELINE_COL_STATUS,
    PIPELINE_COL_CREATED,
    PIPELINE_COL_CHECKLIST,
]

CLOSED_HEADERS = [
    CLOSED_COL_ISSUER,
    CLOSED_COL_TYPE,
    CLOSED_COL_ISSUER_TYPE,
    CLOSED_COL_QUANTUM,
    CLOSED_COL_ISIN,
    CLOSED_COL_COUPON,
    CLOSED_COL_TENOR,
    CLOSED_COL_RATING,
    CLOSED_COL_SECURITY,
    CLOSED_COL_ISSUE_DATE,
    CLOSED_COL_MATURITY,
]

# ===== NUMBER / DATE FORMATS =====
NUMBER_FORMATS = {
    "Amount":     "#,##0.00",
    "Percentage": "0.00%",
    "Integer":    "0",
    "Date":       "DD/MM/YYYY",
    "Text":       "@"
}

COLUMN_WIDTHS = {
    PIPELINE_COL_ISSUER:      30,
    PIPELINE_COL_TYPE:        16,
    PIPELINE_COL_ISSUER_TYPE: 10,
    PIPELINE_COL_QUANTUM:     18,
    PIPELINE_COL_DATE:        22,
    PIPELINE_COL_CREDIT:      22,
    PIPELINE_COL_RATING:      12,
    PIPELINE_COL_SECURITY:    30,
    PIPELINE_COL_STATUS:      15,
    PIPELINE_COL_CREATED:     15,
    PIPELINE_COL_CHECKLIST:   20,
    CLOSED_COL_ISIN:          15,
    CLOSED_COL_COUPON:        15,
    CLOSED_COL_TENOR:         15,
    CLOSED_COL_MATURITY:      15,
    CLOSED_COL_ISSUER_TYPE:   10,
}

# ===== DATE PARSING UTILITY =====
_MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10,
    'november': 11, 'december': 12,
}

def parse_excel_date(value, year=2026):
    """
    Parse various date formats including bare month names like 'Mar', 'Apr'.
    Month names → last day of that month in `year` (e.g. Mar → 31-03-2026).
    """
    if value is None:
        return date.today()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, 'to_pydatetime'):   # pandas Timestamp
        return value.to_pydatetime().date()

    s = str(value).strip()

    # Bare month name  e.g. "Mar", "April"
    key = s.lower()
    if key in _MONTH_MAP:
        month = _MONTH_MAP[key]
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, last_day)

    # Common date string formats
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d-%b-%Y',
                '%d %b %Y', '%b %Y', '%B %Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass

    return date.today()


def parse_coupon(value):
    """Parse coupon values that may come in as '12.10%' or 12.10."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().rstrip('%')
    try:
        return float(s)
    except ValueError:
        return 0.0


def normalise_instrument_type(raw):
    """Map 'Listed' / 'Unlisted' to 'Listed NCD' / 'Unlisted NCD'."""
    if raw is None:
        return "Listed NCD"
    s = str(raw).strip()
    if s.lower().startswith("listed") and "unlisted" not in s.lower():
        return "Listed NCD"
    if s.lower().startswith("unlisted"):
        return "Unlisted NCD"
    # already in correct form
    return s if "NCD" in s else s + " NCD"


# ===== CHECKLIST ITEMS (compressed: 3-5 per phase) =====
# Each entry: (task_title, maker, timing_note, listed_only_flag)

CHECKLIST_ITEMS = {
    "Pre-Exec": [
        # 5 items
        ("Final Term Sheet & costing sheet confirmed",
         "Yubi & Issuer",   "",                   False),
        ("Board & Shareholder Resolutions + Form MGT-14 filed",
         "Issuer",          "Pre T",              False),
        ("Credit Rating letter & Audited Financials in place",
         "Issuer",          "≤1 yr listed; ≤6 mo unlisted", False),
        ("KYC verified; NSDL/CDSL depository agreements executed",
         "Issuer",          "Pre T",              False),
        ("SCORES registration & BSE In-principle approval",
         "Issuer",          "Listed only",        True),
    ],
    "Depo & Stamp": [
        # 3 items
        ("Tripartite agreement with NSDL/CDSL executed; ISIN created",
         "Issuer / RTA",    "T-8 to T-3",        False),
        ("Stamp duty confirmed (quantum & state); stamp paper procured",
         "Issuer / DT",     "T-4 / T-3",         False),
        ("BSE In-principle approval received",
         "Issuer",          "Listed only, T-6",  True),
    ],
    "Docs & EBP": [
        # 4 items
        ("DTA, DTD & DOH executed (Trust & Security docs)",
         "Issuer / Legal",  "T-2",               False),
        ("GID, KID & Private Placement Offer Letter (PAS-4) in place",
         "Issuer / Legal",  "Listed only, T-2",  True),
        ("Issuer Certificate & Rating confirmation letter ready",
         "Issuer",          "T-1",               False),
        ("EBP platform setup complete; pay-in / funding confirmed",
         "Yubi",            "T-1",               False),
    ],
    "T-Day": [
        # 3 items
        ("EBP bidding & provisional allotment completed",
         "Investors / Yubi", "T-1",              False),
        ("Pay-in / Funding received and confirmed",
         "Clearing Corp",   "T",                 False),
        ("Board Meeting held; NCDs allotted & credited to demat accounts",
         "Issuer / R&T",    "T",                 False),
    ],
    "Post": [
        # 4 items
        ("Listing approved on BSE; Intimation sent to Exchange",
         "BSE / Issuer",    "Listed only, T+1",  True),
        ("CHG-9, MGT-14 & PAS-3 filed with ROC",
         "Issuer",          "Within T+30 days",  False),
        ("DT Certificate & Corporate Action processed; demat credits confirmed",
         "Trustee / RTA",   "T+1",               False),
        ("First coupon payment configured; final security creation confirmed",
         "Issuer / Trustee", "T+15 to T+30",     False),
    ],
}

PHASE_TIMINGS = {
    "Pre-Exec":    "Weeks before T",
    "Depo & Stamp": "T-12 to T-3",
    "Docs & EBP":  "T-3 to T-1",
    "T-Day":       "T-1 to T",
    "Post":        "T+1 to T+30",
}

PHASE_DESCRIPTIONS = {
    "Pre-Exec":    "Pre-Execution Setup — Initial documentation and approvals",
    "Depo & Stamp": "Depository, BSE & Stamp Duty — Regulatory registrations",
    "Docs & EBP":  "Document Execution & EBP Setup — Final documentation",
    "T-Day":       "Funding Day — Fund receipt and allotment execution",
    "Post":        "Post-Issuance — Regulatory filings and listing completion",
}


def get_checklist_for_instrument(instrument_type):
    """Return checklist items filtered for Listed or Unlisted NCD."""
    is_listed = ("listed" in instrument_type.lower() and "unlisted" not in instrument_type.lower())
    filtered = {}
    for phase, items in CHECKLIST_ITEMS.items():
        filtered[phase] = [
            (task, maker, timing, lo)
            for task, maker, timing, lo in items
            if not lo or is_listed
        ]
    return filtered


def get_total_steps(instrument_type):
    filtered = get_checklist_for_instrument(instrument_type)
    return sum(len(v) for v in filtered.values())


def get_phase_step_count(phase, instrument_type):
    filtered = get_checklist_for_instrument(instrument_type)
    return len(filtered.get(phase, []))
