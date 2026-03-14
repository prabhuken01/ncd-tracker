"""
NCD Tracker - Validators
Functions for validating user inputs
"""

import re
from datetime import date, datetime
import config

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_company_name(name):
    """
    Validate company name
    
    Args:
        name (str): Company name
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or len(name.strip()) == 0:
        return False, "Company name is required"
    
    if len(name) < 3:
        return False, "Company name must be at least 3 characters"
    
    if len(name) > 100:
        return False, "Company name must be less than 100 characters"
    
    return True, ""

def validate_amount(amount):
    """
    Validate issuance amount
    
    Args:
        amount (float): Amount in crores
    
    Returns:
        tuple: (is_valid, error_message)
    """
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
    """
    Validate coupon/interest rate
    
    Args:
        coupon (float): Coupon rate in %
    
    Returns:
        tuple: (is_valid, error_message)
    """
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
    """
    Validate tenor in months
    
    Args:
        tenor (int): Tenor in months
    
    Returns:
        tuple: (is_valid, error_message)
    """
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
    """
    Validate ISIN format (12 characters: IN + 10 alphanumeric)
    
    Args:
        isin (str): ISIN code
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isin or len(isin.strip()) == 0:
        return False, "ISIN is required"
    
    isin = isin.strip().upper()
    
    # Check length
    if len(isin) != 12:
        return False, "ISIN must be exactly 12 characters"
    
    # Check format: starts with IN, followed by 10 alphanumeric characters
    pattern = r'^IN[A-Z0-9]{10}$'
    if not re.match(pattern, isin):
        return False, "Invalid ISIN format (should be: IN followed by 10 alphanumeric characters)"
    
    return True, ""

def validate_date(date_value, field_name="Date"):
    """
    Validate date
    
    Args:
        date_value (date or str): Date to validate
        field_name (str): Name of field for error message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if date_value is None:
        return False, f"{field_name} is required"
    
    if isinstance(date_value, str):
        try:
            datetime.strptime(date_value, config.DATE_FORMAT)
        except ValueError:
            return False, f"{field_name} must be in {config.DATE_INPUT_FORMAT} format"
    
    return True, ""

def validate_funding_date(funding_date):
    """
    Validate funding date (should be in future)
    
    Args:
        funding_date (date): Funding date
    
    Returns:
        tuple: (is_valid, error_message)
    """
    is_valid, error_msg = validate_date(funding_date, "Funding Date")
    if not is_valid:
        return is_valid, error_msg
    
    if isinstance(funding_date, str):
        funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
    
    # Check if date is not too far in past (allow some flexibility)
    days_diff = (funding_date - date.today()).days
    if days_diff < -90:
        return False, "Funding date cannot be more than 90 days in the past"
    
    return True, ""

def validate_dropdown_selection(value, options, field_name):
    """
    Validate dropdown selection
    
    Args:
        value (str): Selected value
        options (list): List of valid options
        field_name (str): Name of field
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not value or value.strip() == "":
        return False, f"{field_name} is required"
    
    if value not in options:
        return False, f"Invalid {field_name} selection"
    
    return True, ""

def validate_new_deal_form(form_data):
    """
    Validate entire new deal form
    
    Args:
        form_data (dict): Dictionary of form field values
    
    Returns:
        tuple: (is_valid, list of error messages)
    """
    errors = []
    
    # Validate each field
    is_valid, msg = validate_company_name(form_data.get('company_name', ''))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_dropdown_selection(
        form_data.get('instrument_type', ''),
        config.INSTRUMENT_TYPES,
        "Instrument Type"
    )
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_dropdown_selection(
        form_data.get('asset_class', ''),
        config.ASSET_CLASSES,
        "Asset Class"
    )
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_amount(form_data.get('issuance_size', 0))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_funding_date(form_data.get('funding_date'))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_dropdown_selection(
        form_data.get('rating', ''),
        config.RATING_OPTIONS,
        "Rating"
    )
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_dropdown_selection(
        form_data.get('security', ''),
        config.SECURITY_TYPES,
        "Security Type"
    )
    if not is_valid:
        errors.append(msg)
    
    return len(errors) == 0, errors

def validate_closure_form(form_data):
    """
    Validate deal closure form
    
    Args:
        form_data (dict): Dictionary of closure form field values
    
    Returns:
        tuple: (is_valid, list of error messages)
    """
    errors = []
    
    is_valid, msg = validate_isin(form_data.get('isin', ''))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_coupon_rate(form_data.get('coupon', 0))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_tenor(form_data.get('tenor', 0))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg = validate_date(form_data.get('maturity_date'), "Maturity Date")
    if not is_valid:
        errors.append(msg)
    
    return len(errors) == 0, errors
