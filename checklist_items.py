"""
NCD Tracker - Checklist Items Definitions
Complete checklist structure for all 5 phases of NCD issuance
"""

# ===== CHECKLIST STRUCTURE =====
# Each item: (task_title, maker, timing_note, listed_only_flag)

CHECKLIST_ITEMS = {
    "Pre-Exec": [
        ("Final Term Sheet & Costing sheet in place", "Yubi & Issuer", "", False),
        ("Board Resolution — authorising issue of debentures", "Issuer", "", False),
        ("Shareholder Resolution (Sec 180(1)(a),(1)(c),42) + Form MGT-14", "Issuer", "", False),
        ("Board Resolution — authorising allotment", "Issuer", "", False),
        ("Application money account in place", "Issuer", "", False),
        ("Unallocated Credit Rating available", "Issuer", "≤1 yr (listed); ≤6 mo (unlisted)", False),
        ("Audited Financials (last 3 yrs + 6 mo limited review)", "Issuer", "", False),
        ("NSDL and CDSL Agreements (Issuer)", "Issuer", "", False),
        ("Stamp duty payment confirmation (Issuer)", "Issuer", "", False),
        ("Scores Regn & In-principle approval form BSE (only for Listed issuance)", "Issuer", "", True),
        ("NBFC: DOH (Deed of Hypothecation) draft prepared", "Legal", "For NBFC only", False),
        ("Corporate: Mortgage Deed draft prepared", "Legal", "For Corporate only", False),
        ("Rating Letter received and available", "Issuer", "", False),
        ("KYC documents verified and complete", "Issuer", "", False),
    ],
    
    "Depo & Stamp": [
        ("Tripartite agreement with NSDL/CDSL (Issuer & RTA) executed", "Issuer / RTA", "8-12 days", False),
        ("ISIN created and in place from NSDL/CDSL", "Issuer", "T-4 / T-3", False),
        ("BSE SCORES registration done", "Issuer", "Listed only", True),
        ("In-principle approval received from BSE Exchange", "Issuer", "Listed only, 6-10 days", True),
        ("Stamp duty confirmation (quantum & state confirmed)", "Issuer", "T-4 / T-3", False),
        ("Procurement of stamp paper done", "Issuer / DT", "T-3 / T-2", False),
        ("GID and KID (For listed issuance)", "Issuer", "T-2", True),
    ],
    
    "Docs & EBP": [
        ("Signed GID (Group Information Document) & IPA in place", "Issuer", "Listed only, T-2", True),
        ("Signed KID (Key Information Document) in place", "Issuer", "Listed only, T-2", True),
        ("DTA (Debenture Trust Agreement) executed", "Issuer", "T-2", False),
        ("DTD (Debenture Trust Deed) executed", "Issuer", "T-2", False),
        ("DOH (Declaration of Hypothecation) executed", "Issuer", "T-2", False),
        ("Signed Issuer Certificate in place", "Issuer", "T-1", False),
        ("Private Placement Offer Letter (Form PAS 4) (Legal Counsel)", "Legal Counsel", "", False),
        ("Payin / Funding received and confirmed (Yubi)", "Yubi", "", False),
        ("Demat credit to investors (Registrar)", "Registrar", "", False),
        ("Rating confirmation letter", "Issuer", "T-2", False),
        ("Security creation documents signed", "Issuer", "T-2", False),
    ],
    
    "T-Day": [
        ("EBP bidding, provisional allotment, Issue Open & Close completed", "Investors / Yubi", "T-1", False),
        ("Pay-in / Funding received and confirmed", "Clearing Corp", "T", False),
        ("Board Meeting held for allotment of NCDs", "Issuer", "T", False),
        ("Securities credited to investor demat accounts", "Issuer / R&T", "T", False),
        ("Intimation sent to Stock Exchange", "Issuer", "Listed only, T+1", True),
    ],
    
    "Post": [
        ("Annexure B + Debenture Trustee Certificate delivered", "Trustee", "T+1", False),
        ("Listing approved and confirmed on BSE", "BSE", "Listed only, T+2", True),
        ("Corporate Action for allotment credit processed", "RTA", "T+1", False),
        ("Charge Creation & CHG-9 filing with ROC", "Issuer", "Within T+30 cal days", False),
        ("BSE Listing Agreement executed", "Issuer", "Listed only", True),
        ("Form MGT-14 filed with ROC", "Issuer", "Within T+30 cal days", False),
        ("Form PAS-3 filed with ROC", "Issuer", "Within 15 days", False),
        ("Debenture certificates issued to investors", "RTA", "Within 2 months", False),
        ("First coupon payment setup configured", "Issuer", "T+15", False),
        ("Final security creation confirmation", "Trustee", "T+30", False),
    ]
}

# ===== PHASE TIMINGS =====
PHASE_TIMINGS = {
    "Pre-Exec": "Weeks before T",
    "Depo & Stamp": "T-12 to T-3",
    "Docs & EBP": "T-3 to T-1",
    "T-Day": "T-1 to T",
    "Post": "T+1 to T+30"
}

# ===== PHASE DESCRIPTIONS =====
PHASE_DESCRIPTIONS = {
    "Pre-Exec": "Pre-Execution Setup - Initial documentation and approvals",
    "Depo & Stamp": "Depository, BSE & Stamp Duty - Regulatory registrations and clearances",
    "Docs & EBP": "Document Execution & EBP Setup - Final documentation and electronic bidding",
    "T-Day": "Funding Day - Fund receipt and allotment execution",
    "Post": "Post-Issuance - Regulatory filings and listing completion"
}

def get_checklist_for_instrument(instrument_type):
    """
    Return checklist items filtered by instrument type
    
    Args:
        instrument_type (str): "Listed NCD" or "Unlisted NCD"
    
    Returns:
        dict: Filtered checklist items
    """
    is_listed = (instrument_type == "Listed NCD")
    
    filtered_checklist = {}
    for phase, items in CHECKLIST_ITEMS.items():
        filtered_items = []
        for task, maker, timing, listed_only in items:
            # Include item if: not listed-only OR is listed issuance
            if not listed_only or is_listed:
                filtered_items.append((task, maker, timing, listed_only))
        filtered_checklist[phase] = filtered_items
    
    return filtered_checklist

def get_total_steps(instrument_type):
    """
    Get total number of checklist steps for given instrument type
    
    Args:
        instrument_type (str): "Listed NCD" or "Unlisted NCD"
    
    Returns:
        int: Total number of steps
    """
    filtered = get_checklist_for_instrument(instrument_type)
    return sum(len(items) for items in filtered.values())

def get_phase_step_count(phase, instrument_type):
    """
    Get number of steps in a specific phase for given instrument type
    
    Args:
        phase (str): Phase name
        instrument_type (str): "Listed NCD" or "Unlisted NCD"
    
    Returns:
        int: Number of steps in phase
    """
    filtered = get_checklist_for_instrument(instrument_type)
    return len(filtered.get(phase, []))
