"""
NCD Tracker - Formatters
Functions for formatting data display
"""

from datetime import date, datetime, timedelta
import config

def format_amount(amount):
    """
    Format amount in Rs Crore with 2 decimal places
    
    Args:
        amount (float): Amount in crores
    
    Returns:
        str: Formatted string like "₹500.00 Cr"
    """
    if amount is None:
        return "N/A"
    return f"{config.AMOUNT_UNIT}{amount:,.{config.AMOUNT_DECIMAL_PLACES}f}"

def format_percentage(value):
    """
    Format percentage with 2 decimal places
    
    Args:
        value (float): Percentage value (e.g., 9.75 for 9.75%)
    
    Returns:
        str: Formatted string like "9.75%"
    """
    if value is None:
        return "N/A"
    return f"{value:.{config.INTEREST_DECIMAL_PLACES}f}%"

def format_date(date_obj, include_day_name=False):
    """
    Format date as DD/MM/YYYY
    
    Args:
        date_obj (date): Date object
        include_day_name (bool): Include day of week
    
    Returns:
        str: Formatted date string
    """
    if date_obj is None:
        return "N/A"
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, config.DATE_FORMAT).date()
        except:
            return date_obj
    
    formatted = date_obj.strftime(config.DATE_FORMAT)
    
    if include_day_name:
        day_name = date_obj.strftime("%A")
        formatted = f"{day_name}, {formatted}"
    
    return formatted

def format_t_countdown(funding_date):
    """
    Format T-day countdown (e.g., "T-14d" or "T+2d")
    
    Args:
        funding_date (date): Funding date
    
    Returns:
        str: Formatted countdown string
    """
    if funding_date is None:
        return "N/A"
    
    if isinstance(funding_date, str):
        try:
            funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
        except:
            return "N/A"
    
    delta = funding_date - date.today()
    days = delta.days
    
    if days < 0:
        return f"T+{abs(days)}d"
    elif days == 0:
        return "T-Day"
    else:
        return f"T-{days}d"

def format_progress(completed, total):
    """
    Format progress as "X/Y - Z%"
    
    Args:
        completed (int): Completed steps
        total (int): Total steps
    
    Returns:
        str: Formatted progress string
    """
    if total == 0:
        percentage = 0
    else:
        percentage = round((completed / total) * 100)
    
    return f"{completed}/{total} - {percentage}%"

def format_tenor(months):
    """
    Format tenor in months (e.g., "24 Months")
    
    Args:
        months (int): Number of months
    
    Returns:
        str: Formatted tenor string
    """
    if months is None:
        return "N/A"
    return f"{months} Month{'s' if months != 1 else ''}"

def format_isin(isin):
    """
    Format ISIN with spacing for readability (e.g., "INE123456789")
    
    Args:
        isin (str): ISIN code
    
    Returns:
        str: Formatted ISIN
    """
    if isin is None or len(isin) != 12:
        return isin if isin else "N/A"
    
    # Format as INE 123456 789
    return f"{isin[:3]} {isin[3:9]} {isin[9:]}"

def get_t_countdown_color(funding_date):
    """
    Get color category based on days to funding
    
    Args:
        funding_date (date): Funding date
    
    Returns:
        str: Color category ('critical', 'warning', or 'normal')
    """
    if funding_date is None:
        return "normal"
    
    if isinstance(funding_date, str):
        try:
            funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
        except:
            return "normal"
    
    delta = funding_date - date.today()
    days = delta.days
    
    if days <= 7:
        return "critical"
    elif days <= 14:
        return "warning"
    else:
        return "normal"

def get_status_emoji(status):
    """
    Get emoji for status
    
    Args:
        status (str): Status value
    
    Returns:
        str: Emoji character
    """
    status_emojis = {
        "Pending": "⏳",
        "In Progress": "⚡",
        "Completed": "✅",
        "Blocked": "🚫"
    }
    return status_emojis.get(status, "")

def calculate_maturity_date(funding_date, tenor_months):
    """
    Calculate maturity date from funding date and tenor
    
    Args:
        funding_date (date): Funding date
        tenor_months (int): Tenor in months
    
    Returns:
        date: Maturity date
    """
    if isinstance(funding_date, str):
        funding_date = datetime.strptime(funding_date, config.DATE_FORMAT).date()
    
    # Approximate month addition (may need adjustment for month-end dates)
    days_to_add = tenor_months * 30
    return funding_date + timedelta(days=days_to_add)

def format_file_size(size_bytes):
    """
    Format file size in human-readable format
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted size (e.g., "2.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
