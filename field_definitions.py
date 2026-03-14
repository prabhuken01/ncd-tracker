"""
NCD Tracker - Field Definitions
Excel column mappings and data type specifications
"""

# ===== PIPELINE ISSUANCE SHEET STRUCTURE =====
PIPELINE_FIELDS = {
    "Company Name": {"col": "A", "dtype": str, "required": True},
    "Instrument Type": {"col": "B", "dtype": str, "required": True},
    "Asset Class": {"col": "C", "dtype": str, "required": True},
    "Issuance Size (₹ Cr)": {"col": "D", "dtype": float, "required": True},
    "Funding Date (T)": {"col": "E", "dtype": "date", "required": True},
    "Rating": {"col": "F", "dtype": str, "required": True},
    "Security": {"col": "G", "dtype": str, "required": True},
    "Checklist Progress": {"col": "H", "dtype": str, "required": False},  # Calculated field
    "Created Date": {"col": "I", "dtype": "date", "required": False},
    "Status": {"col": "J", "dtype": str, "required": False},  # Auto: In Progress/Fully Funded
}

# ===== CLOSED NCD DEAL SHEET STRUCTURE =====
CLOSED_FIELDS = {
    "Company Name": {"col": "A", "dtype": str, "required": True},
    "Instrument Type": {"col": "B", "dtype": str, "required": True},
    "Asset Class": {"col": "C", "dtype": str, "required": True},
    "Issuance Size (₹ Cr)": {"col": "D", "dtype": float, "required": True},
    "ISIN": {"col": "E", "dtype": str, "required": True},
    "Coupon (% p.a.)": {"col": "F", "dtype": float, "required": True},
    "Tenor (Months)": {"col": "G", "dtype": int, "required": True},
    "Rating": {"col": "H", "dtype": str, "required": True},
    "Security": {"col": "I", "dtype": str, "required": True},
    "Funding Date": {"col": "J", "dtype": "date", "required": True},
    "Maturity Date": {"col": "K", "dtype": "date", "required": True},
}

# ===== HEADER ROW DEFINITIONS =====
PIPELINE_HEADERS = list(PIPELINE_FIELDS.keys())
CLOSED_HEADERS = list(CLOSED_FIELDS.keys())

# ===== DEFAULT VALUES =====
DEFAULT_VALUES = {
    "Checklist Progress": "0/0 - 0%",
    "Status": "In Progress",
    "Created Date": "TODAY"
}

# ===== VALIDATION MAPPINGS =====
FIELD_VALIDATORS = {
    "Company Name": {
        "min_length": 3,
        "max_length": 100,
        "pattern": None
    },
    "Issuance Size (₹ Cr)": {
        "min": 1,
        "max": 10000,
        "decimals": 2
    },
    "Coupon (% p.a.)": {
        "min": 0.0,
        "max": 25.0,
        "decimals": 2
    },
    "Tenor (Months)": {
        "min": 1,
        "max": 120
    },
    "ISIN": {
        "pattern": r"^IN[A-Z0-9]{10}$",  # Standard ISIN format
        "length": 12
    }
}

# ===== EXCEL FORMATTING STYLES =====
HEADER_STYLE = {
    "font": {"bold": True, "size": 11, "color": "FFFFFF"},
    "fill": {"pattern": "solid", "start_color": "366092"},
    "alignment": {"horizontal": "center", "vertical": "center"},
    "border": True
}

DATA_STYLE = {
    "font": {"size": 10},
    "alignment": {"horizontal": "left", "vertical": "center"},
    "border": True
}

NUMBER_FORMATS = {
    "Amount": '₹#,##0.00',
    "Percentage": '0.00%',
    "Integer": '0',
    "Date": 'DD/MM/YYYY',
    "Text": '@'
}

# ===== COLUMN WIDTHS (in Excel units) =====
COLUMN_WIDTHS = {
    "Company Name": 30,
    "Instrument Type": 15,
    "Asset Class": 18,
    "Issuance Size (₹ Cr)": 18,
    "Funding Date (T)": 15,
    "Rating": 12,
    "Security": 40,
    "Checklist Progress": 20,
    "Created Date": 15,
    "Status": 15,
    "ISIN": 15,
    "Coupon (% p.a.)": 15,
    "Tenor (Months)": 15,
    "Maturity Date": 15
}

# ===== LOOKUP FUNCTIONS =====
def get_column_letter(field_name, sheet_type="pipeline"):
    """Get Excel column letter for a field name"""
    fields = PIPELINE_FIELDS if sheet_type == "pipeline" else CLOSED_FIELDS
    return fields.get(field_name, {}).get("col")

def get_data_type(field_name, sheet_type="pipeline"):
    """Get data type for a field name"""
    fields = PIPELINE_FIELDS if sheet_type == "pipeline" else CLOSED_FIELDS
    return fields.get(field_name, {}).get("dtype")

def is_required_field(field_name, sheet_type="pipeline"):
    """Check if a field is required"""
    fields = PIPELINE_FIELDS if sheet_type == "pipeline" else CLOSED_FIELDS
    return fields.get(field_name, {}).get("required", False)
