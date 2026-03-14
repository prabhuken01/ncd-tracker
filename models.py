"""
NCD Tracker - Models
Merged: data_models + validators
Data classes for PipelineDeal, ClosedDeal, checklist items, and all validators.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional
import json
import config


# ══════════════════════════════════════════════════
#  DATA MODELS
# ══════════════════════════════════════════════════

@dataclass
class ChecklistItem:
    step_number: int
    task_title:  str
    maker:       str
    timing_note: str
    status:      str  = "Pending"
    completed:   bool = False
    sub_notes:   str  = ""
    listed_only: bool = False

    def to_dict(self):
        return {
            "step_number": self.step_number,
            "task_title":  self.task_title,
            "maker":       self.maker,
            "timing_note": self.timing_note,
            "status":      self.status,
            "completed":   self.completed,
            "sub_notes":   self.sub_notes,
            "listed_only": self.listed_only,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class PhaseChecklist:
    phase_name: str
    items: List[ChecklistItem] = field(default_factory=list)

    def get_completed_count(self):
        return sum(1 for i in self.items if i.completed)

    def get_total_count(self):
        return len(self.items)

    def get_completion_percentage(self):
        total = self.get_total_count()
        if total == 0:
            return 0
        return round((self.get_completed_count() / total) * 100)

    def to_dict(self):
        return {"phase_name": self.phase_name, "items": [i.to_dict() for i in self.items]}

    @classmethod
    def from_dict(cls, data):
        phase = cls(phase_name=data["phase_name"])
        phase.items = [ChecklistItem.from_dict(i) for i in data["items"]]
        return phase


@dataclass
class PipelineDeal:
    """Active deal in the issuance pipeline."""
    company_name:      str
    instrument_type:   str          # "Listed NCD" / "Unlisted NCD"
    issuer_type:       str          # "FS" / "EF"
    asset_class:       str          # "NBFC", "Housing Finance", etc.
    issuance_size:     float
    funding_date:      date
    rating:            str  = "N/A"
    security:          str  = "Unsecured"
    checklist_progress: str = "0/0 - 0%"
    created_date:      Optional[date] = None
    status:            str  = "In Progress"
    checklists:        Dict[str, PhaseChecklist] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_date is None:
            self.created_date = date.today()
        if isinstance(self.funding_date, str):
            self.funding_date = datetime.strptime(self.funding_date, "%d/%m/%Y").date()
        if isinstance(self.created_date, str):
            self.created_date = datetime.strptime(self.created_date, "%d/%m/%Y").date()

    # ── progress helpers ─────────────────────────────────────────────────────
    def get_total_completed_steps(self):
        return sum(c.get_completed_count() for c in self.checklists.values())

    def get_total_steps(self):
        return sum(c.get_total_count() for c in self.checklists.values())

    def get_overall_completion_percentage(self):
        total = self.get_total_steps()
        if total == 0:
            return 0
        return round((self.get_total_completed_steps() / total) * 100)

    def update_checklist_progress(self):
        completed  = self.get_total_completed_steps()
        total      = self.get_total_steps()
        percentage = self.get_overall_completion_percentage()
        self.checklist_progress = f"{completed}/{total} · {percentage}%"

    # ── T-day helpers ─────────────────────────────────────────────────────────
    def get_days_until_funding(self):
        return (self.funding_date - date.today()).days

    def get_t_countdown_color(self):
        days = self.get_days_until_funding()
        if days <= 7:
            return "critical"
        elif days <= 21:
            return "warning"
        return "normal"

    def is_fully_funded(self):
        return self.get_overall_completion_percentage() == 100

    # ── Excel row ─────────────────────────────────────────────────────────────
    def to_excel_row(self):
        return [
            self.company_name,
            self.instrument_type,
            self.issuer_type,
            self.issuance_size,
            self.funding_date,
            self.status,
            self.rating,
            self.security,
            self.status,
            self.created_date,
            "",            # Checklist Data – written separately
        ]


@dataclass
class ClosedDeal:
    """Archived (funded & closed) NCD deal."""
    company_name:    str
    instrument_type: str
    issuer_type:     str
    asset_class:     str
    issuance_size:   float
    isin:            str
    coupon:          float
    tenor:           int
    rating:          str
    security:        str
    funding_date:    date
    maturity_date:   date

    def __post_init__(self):
        if isinstance(self.funding_date, str):
            self.funding_date = datetime.strptime(self.funding_date, "%d/%m/%Y").date()
        if isinstance(self.maturity_date, str):
            self.maturity_date = datetime.strptime(self.maturity_date, "%d/%m/%Y").date()

    def get_days_to_maturity(self):
        return (self.maturity_date - date.today()).days

    def to_excel_row(self):
        return [
            self.company_name,
            self.instrument_type,
            self.issuer_type,
            self.issuance_size,
            self.isin,
            self.coupon,
            self.tenor,
            self.rating,
            self.security,
            self.funding_date,
            self.maturity_date,
        ]

    @classmethod
    def from_pipeline_deal(cls, pipeline_deal, isin, coupon, tenor, maturity_date):
        return cls(
            company_name    = pipeline_deal.company_name,
            instrument_type = pipeline_deal.instrument_type,
            issuer_type     = pipeline_deal.issuer_type,
            asset_class     = pipeline_deal.asset_class,
            issuance_size   = pipeline_deal.issuance_size,
            isin            = isin,
            coupon          = coupon,
            tenor           = tenor,
            rating          = pipeline_deal.rating,
            security        = pipeline_deal.security,
            funding_date    = pipeline_deal.funding_date,
            maturity_date   = maturity_date,
        )


# ══════════════════════════════════════════════════
#  VALIDATORS
# ══════════════════════════════════════════════════

class ValidationError(Exception):
    pass


def validate_company_name(name):
    if not name or not name.strip():
        return False, "Company name is required"
    if len(name) < 3:
        return False, "Company name must be at least 3 characters"
    if len(name) > 100:
        return False, "Company name must be less than 100 characters"
    return True, ""


def validate_amount(amount):
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return False, "Amount must be a valid number"
    if amount < config.MIN_ISSUANCE_SIZE:
        return False, f"Amount must be at least {config.AMOUNT_UNIT}{config.MIN_ISSUANCE_SIZE}"
    if amount > config.MAX_ISSUANCE_SIZE:
        return False, f"Amount must not exceed {config.AMOUNT_UNIT}{config.MAX_ISSUANCE_SIZE}"
    return True, ""


def validate_coupon_rate(coupon):
    try:
        coupon = float(coupon)
    except (ValueError, TypeError):
        return False, "Coupon rate must be a valid number"
    if coupon < config.MIN_COUPON_RATE:
        return False, f"Coupon rate must be at least {config.MIN_COUPON_RATE}%"
    if coupon > config.MAX_COUPON_RATE:
        return False, f"Coupon rate must not exceed {config.MAX_COUPON_RATE}%"
    return True, ""


def validate_tenor(tenor):
    try:
        tenor = int(tenor)
    except (ValueError, TypeError):
        return False, "Tenor must be a valid integer"
    if tenor < config.MIN_TENOR_MONTHS:
        return False, f"Tenor must be at least {config.MIN_TENOR_MONTHS} month"
    if tenor > config.MAX_TENOR_MONTHS:
        return False, f"Tenor must not exceed {config.MAX_TENOR_MONTHS} months"
    return True, ""


def validate_isin(isin):
    if not isin or not isin.strip():
        return False, "ISIN is required"
    isin = isin.strip().upper()
    if len(isin) != 12:
        return False, "ISIN must be exactly 12 characters"
    if not re.match(r'^IN[A-Z0-9]{10}$', isin):
        return False, "Invalid ISIN format (IN followed by 10 alphanumeric chars)"
    return True, ""


def validate_date(date_value, field_name="Date"):
    if date_value is None:
        return False, f"{field_name} is required"
    if isinstance(date_value, str):
        try:
            datetime.strptime(date_value, config.DATE_FORMAT)
        except ValueError:
            return False, f"{field_name} must be in {config.DATE_INPUT_FORMAT} format"
    return True, ""


def validate_funding_date(funding_date):
    ok, msg = validate_date(funding_date, "Funding Date")
    if not ok:
        return ok, msg
    if isinstance(funding_date, str):
        funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
    if (funding_date - date.today()).days < -90:
        return False, "Funding date cannot be more than 90 days in the past"
    return True, ""


def validate_dropdown_selection(value, options, field_name):
    if not value or str(value).strip() == "":
        return False, f"{field_name} is required"
    if value not in options:
        return False, f"Invalid {field_name} selection"
    return True, ""


def validate_new_deal_form(form_data):
    errors = []
    checks = [
        validate_company_name(form_data.get('company_name', '')),
        validate_dropdown_selection(form_data.get('instrument_type', ''), config.INSTRUMENT_TYPES, "Instrument Type"),
        validate_dropdown_selection(form_data.get('issuer_type', ''), config.ISSUER_TYPES, "Issuer Type"),
        validate_amount(form_data.get('issuance_size', 0)),
        validate_funding_date(form_data.get('funding_date')),
    ]
    for ok, msg in checks:
        if not ok:
            errors.append(msg)
    return len(errors) == 0, errors


def validate_closure_form(form_data):
    errors = []
    checks = [
        validate_isin(form_data.get('isin', '')),
        validate_coupon_rate(form_data.get('coupon', 0)),
        validate_tenor(form_data.get('tenor', 0)),
        validate_date(form_data.get('maturity_date'), "Maturity Date"),
    ]
    for ok, msg in checks:
        if not ok:
            errors.append(msg)
    return len(errors) == 0, errors
