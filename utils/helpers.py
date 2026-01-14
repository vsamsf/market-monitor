"""Utility helper functions."""

from datetime import datetime, timedelta
from typing import Optional
import pytz


def get_ist_now() -> datetime:
    """Get current datetime in IST timezone."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def utc_to_ist(dt: datetime) -> datetime:
    """Convert UTC datetime to IST."""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    ist = pytz.timezone('Asia/Kolkata')
    return dt.astimezone(ist)


def ist_to_utc(dt: datetime) -> datetime:
    """Convert IST datetime to UTC."""
    ist = pytz.timezone('Asia/Kolkata')
    if dt.tzinfo is None:
        dt = ist.localize(dt)
    return dt.astimezone(pytz.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string."""
    return datetime.strptime(dt_str, format_str)


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format currency amount."""
    return f"{currency}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage value."""
    return f"{value:.{decimals}f}%"


def is_market_open(current_time: Optional[datetime] = None) -> bool:
    """
    Check if market is currently open.
    Market hours: 9:15 AM - 3:30 PM IST on weekdays.
    
    Args:
        current_time: Datetime to check (defaults to now in IST)
    
    Returns:
        True if market is open, False otherwise
    """
    if current_time is None:
        current_time = get_ist_now()
    
    # Check if it's a weekday (0 = Monday, 6 = Sunday)
    if current_time.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check time
    market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_open <= current_time <= market_close


def calculate_change_percent(current: float, previous: float) -> float:
    """Calculate percentage change."""
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_next_weekday(current_date: Optional[datetime] = None) -> datetime:
    """Get next weekday (skip weekends)."""
    if current_date is None:
        current_date = get_ist_now()
    
    next_day = current_date + timedelta(days=1)
    
    # Skip weekends
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    
    return next_day
