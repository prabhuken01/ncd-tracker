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


# ===== CHECKLIST ITEMS =====
# Each entry: (task_title, maker, timing_note, listed_only_flag)

CHECKLIST_ITEMS = {
    "Pre-Exec": [
        ("Final Term Sheet & Costing sheet in place",                           "Yubi & Issuer",  "",                            False),
        ("Board Resolution — authorising issue of debentures",                  "Issuer",         "",                            False),
        ("Shareholder Resolution (Sec 180(1)(a),(1)(c),42) + Form MGT-14",     "Issuer",         "",                            False),
        ("Board Resolution — authorising allotment",                            "Issuer",         "",                            False),
        ("Application money account in place",                                  "Issuer",         "",                            False),
        ("Unallocated Credit Rating available",                                 "Issuer",         "≤1 yr (listed); ≤6 mo (unlisted)", False),
        ("Audited Financials (last 3 yrs + 6 mo limited review)",              "Issuer",         "",                            False),
        ("NSDL and CDSL Agreements (Issuer)",                                   "Issuer",         "",                            False),
        ("Stamp duty payment confirmation (Issuer)",                            "Issuer",         "",                            False),
        ("SCORES Regn & In-principle approval from BSE (Listed only)",         "Issuer",         "",                            True),
        ("NBFC: DOH (Deed of Hypothecation) draft prepared",                   "Legal",          "For NBFC only",               False),
        ("Corporate: Mortgage Deed draft prepared",                             "Legal",          "For Corporate only",          False),
        ("Rating Letter received and available",                                "Issuer",         "",                            False),
        ("KYC documents verified and complete",                                 "Issuer",         "",                            False),
    ],
    "Depo & Stamp": [
        ("Tripartite agreement with NSDL/CDSL (Issuer & RTA) executed",        "Issuer / RTA",   "8-12 days",                   False),
        ("ISIN created and in place from NSDL/CDSL",                           "Issuer",         "T-4 / T-3",                   False),
        ("BSE SCORES registration done",                                        "Issuer",         "Listed only",                 True),
        ("In-principle approval received from BSE Exchange",                    "Issuer",         "Listed only, 6-10 days",      True),
        ("Stamp duty confirmation (quantum & state confirmed)",                 "Issuer",         "T-4 / T-3",                   False),
        ("Procurement of stamp paper done",                                     "Issuer / DT",    "T-3 / T-2",                   False),
        ("GID and KID (For listed issuance)",                                   "Issuer",         "T-2",                         True),
    ],
    "Docs & EBP": [
        ("Signed GID (Group Information Document) & IPA in place",             "Issuer",         "Listed only, T-2",            True),
        ("Signed KID (Key Information Document) in place",                     "Issuer",         "Listed only, T-2",            True),
        ("DTA (Debenture Trust Agreement) executed",                            "Issuer",         "T-2",                         False),
        ("DTD (Debenture Trust Deed) executed",                                 "Issuer",         "T-2",                         False),
        ("DOH (Declaration of Hypothecation) executed",                        "Issuer",         "T-2",                         False),
        ("Signed Issuer Certificate in place",                                  "Issuer",         "T-1",                         False),
        ("Private Placement Offer Letter (Form PAS 4) (Legal Counsel)",        "Legal Counsel",  "",                            False),
        ("Payin / Funding received and confirmed (Yubi)",                      "Yubi",           "",                            False),
        ("Demat credit to investors (Registrar)",                               "Registrar",      "",                            False),
        ("Rating confirmation letter",                                          "Issuer",         "T-2",                         False),
        ("Security creation documents signed",                                  "Issuer",         "T-2",                         False),
    ],
    "T-Day": [
        ("EBP bidding, provisional allotment, Issue Open & Close completed",   "Investors / Yubi", "T-1",                       False),
        ("Pay-in / Funding received and confirmed",                             "Clearing Corp",  "T",                           False),
        ("Board Meeting held for allotment of NCDs",                           "Issuer",         "T",                           False),
        ("Securities credited to investor demat accounts",                      "Issuer / R&T",   "T",                           False),
        ("Intimation sent to Stock Exchange",                                   "Issuer",         "Listed only, T+1",            True),
    ],
    "Post": [
        ("Annexure B + Debenture Trustee Certificate delivered",               "Trustee",        "T+1",                         False),
        ("Listing approved and confirmed on BSE",                              "BSE",            "Listed only, T+2",            True),
        ("Corporate Action for allotment credit processed",                    "RTA",            "T+1",                         False),
        ("Charge Creation & CHG-9 filing with ROC",                            "Issuer",         "Within T+30 cal days",        False),
        ("BSE Listing Agreement executed",                                      "Issuer",         "Listed only",                 True),
        ("Form MGT-14 filed with ROC",                                          "Issuer",         "Within T+30 cal days",        False),
        ("Form PAS-3 filed with ROC",                                           "Issuer",         "Within 15 days",              False),
        ("Debenture certificates issued to investors",                          "RTA",            "Within 2 months",             False),
        ("First coupon payment setup configured",                              "Issuer",         "T+15",                        False),
        ("Final security creation confirmation",                               "Trustee",        "T+30",                        False),
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
