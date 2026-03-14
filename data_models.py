"""
NCD Tracker - Data Models
Python classes for representing deal data
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional
import json

@dataclass
class ChecklistItem:
    """Individual checklist item"""
    step_number: int
    task_title: str
    maker: str
    timing_note: str
    status: str = "Pending"
    completed: bool = False
    sub_notes: str = ""
    listed_only: bool = False
    
    def to_dict(self):
        return {
            "step_number": self.step_number,
            "task_title": self.task_title,
            "maker": self.maker,
            "timing_note": self.timing_note,
            "status": self.status,
            "completed": self.completed,
            "sub_notes": self.sub_notes,
            "listed_only": self.listed_only
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class PhaseChecklist:
    """Checklist for a single phase"""
    phase_name: str
    items: List[ChecklistItem] = field(default_factory=list)
    
    def get_completed_count(self):
        return sum(1 for item in self.items if item.completed)
    
    def get_total_count(self):
        return len(self.items)
    
    def get_completion_percentage(self):
        total = self.get_total_count()
        if total == 0:
            return 0
        return round((self.get_completed_count() / total) * 100)
    
    def to_dict(self):
        return {
            "phase_name": self.phase_name,
            "items": [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data):
        phase = cls(phase_name=data["phase_name"])
        phase.items = [ChecklistItem.from_dict(item) for item in data["items"]]
        return phase

@dataclass
class PipelineDeal:
    """Deal in the pipeline (not yet funded)"""
    company_name: str
    instrument_type: str
    asset_class: str
    issuance_size: float
    funding_date: date
    rating: str
    security: str
    checklist_progress: str = "0/0 - 0%"
    created_date: Optional[date] = None
    status: str = "In Progress"
    checklists: Dict[str, PhaseChecklist] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = date.today()
        if isinstance(self.funding_date, str):
            self.funding_date = datetime.strptime(self.funding_date, "%d/%m/%Y").date()
        if isinstance(self.created_date, str):
            self.created_date = datetime.strptime(self.created_date, "%d/%m/%Y").date()
    
    def get_total_completed_steps(self):
        return sum(checklist.get_completed_count() for checklist in self.checklists.values())
    
    def get_total_steps(self):
        return sum(checklist.get_total_count() for checklist in self.checklists.values())
    
    def get_overall_completion_percentage(self):
        total = self.get_total_steps()
        if total == 0:
            return 0
        return round((self.get_total_completed_steps() / total) * 100)
    
    def update_checklist_progress(self):
        """Update the checklist progress string"""
        completed = self.get_total_completed_steps()
        total = self.get_total_steps()
        percentage = self.get_overall_completion_percentage()
        self.checklist_progress = f"{completed}/{total} - {percentage}%"
    
    def get_days_until_funding(self):
        """Get days remaining until funding date"""
        delta = self.funding_date - date.today()
        return delta.days
    
    def get_t_countdown_color(self):
        """Get color code based on days remaining"""
        days = self.get_days_until_funding()
        if days <= 7:
            return "critical"
        elif days <= 14:
            return "warning"
        else:
            return "normal"
    
    def is_fully_funded(self):
        """Check if all checklist items are completed"""
        return self.get_overall_completion_percentage() == 100
    
    def to_excel_row(self):
        """Convert to Excel row format"""
        return [
            self.company_name,
            self.instrument_type,
            self.asset_class,
            self.issuance_size,
            self.funding_date,
            self.rating,
            self.security,
            self.checklist_progress,
            self.created_date,
            self.status
        ]

@dataclass
class ClosedDeal:
    """Closed deal (fully funded and completed)"""
    company_name: str
    instrument_type: str
    asset_class: str
    issuance_size: float
    isin: str
    coupon: float
    tenor: int
    rating: str
    security: str
    funding_date: date
    maturity_date: date
    
    def __post_init__(self):
        if isinstance(self.funding_date, str):
            self.funding_date = datetime.strptime(self.funding_date, "%d/%m/%Y").date()
        if isinstance(self.maturity_date, str):
            self.maturity_date = datetime.strptime(self.maturity_date, "%d/%m/%Y").date()
    
    def to_excel_row(self):
        """Convert to Excel row format"""
        return [
            self.company_name,
            self.instrument_type,
            self.asset_class,
            self.issuance_size,
            self.isin,
            self.coupon,
            self.tenor,
            self.rating,
            self.security,
            self.funding_date,
            self.maturity_date
        ]
    
    def get_days_to_maturity(self):
        """Get days remaining until maturity"""
        delta = self.maturity_date - date.today()
        return delta.days
    
    @classmethod
    def from_pipeline_deal(cls, pipeline_deal, isin, coupon, tenor, maturity_date):
        """Create ClosedDeal from PipelineDeal"""
        return cls(
            company_name=pipeline_deal.company_name,
            instrument_type=pipeline_deal.instrument_type,
            asset_class=pipeline_deal.asset_class,
            issuance_size=pipeline_deal.issuance_size,
            isin=isin,
            coupon=coupon,
            tenor=tenor,
            rating=pipeline_deal.rating,
            security=pipeline_deal.security,
            funding_date=pipeline_deal.funding_date,
            maturity_date=maturity_date
        )
