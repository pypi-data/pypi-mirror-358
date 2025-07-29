# dtwheel/__init__.py
"""
dtwheel: Intuitive Datetime Manipulation.

A lean, intuitive datetime manipulation library for Python, focusing on
readability and returning native datetime objects.
"""

from datetime import datetime, date, timedelta, time
# zoneinfo is imported indirectly via timezone.py and relative.py,
# but can be directly imported here for clarity if needed for public API types.
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError # Direct import for type hinting and potential direct use in `now` if logic shifts

# Import core functionality from sub-modules
from ._version import __version__
from ._helpers import _convert_to_date, _convert_to_datetime # Helper for internal conversions

# Timezone related imports
from .timezone import set_default_timezone, to_timezone, ensure_aware, ensure_utc, get_default_timezone

# Constants (e.g., weekdays)
from .constants import MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY

# Delta helpers
from .deltas import days, hours, minutes, seconds, weeks, delta, add_months, add_years

# Relative time functions (importing the now/today from here for consistency in relative.py)
# We re-define now/today in this __init__.py to ensure they are the main public entry points
# and can call the timezone logic directly, or delegate.
# For circular dependency avoidance, now/today logic is in relative.py and then imported/re-exported.
# However, to explicitly use timezone.py logic, we re-implement them here.

def now(tz: str = None) -> datetime:
    """
    Returns the current datetime.

    If `tz` is provided, returns the current datetime in that specific timezone.
    If `tz` is None and a default timezone has been set (via `set_default_timezone`),
    returns an aware datetime in the default timezone.
    If no timezone is specified and no default is set, returns a naive datetime.

    Args:
        tz (str, optional): The timezone string (e.g., 'UTC', 'America/New_York').

    Returns:
        datetime: The current datetime object.
    """
    if tz:
        try:
            return datetime.now(ZoneInfo(tz))
        except ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone string: '{tz}'")

    default_tz_obj = get_default_timezone()
    if default_tz_obj:
        return datetime.now(default_tz_obj)
    return datetime.now() # Returns naive datetime if no default timezone found/set

def today(tz: str = None) -> date:
    """
    Returns today's date.

    If `tz` is provided, returns today's date considering that timezone.
    If `tz` is None, uses the same timezone logic as `dtwheel.now()`.

    Args:
        tz (str, optional): The timezone string.

    Returns:
        date: Today's date.
    """
    return now(tz=tz).date()

# Import other relative time functions from their module
from .relative import (
    tomorrow, yesterday,
    next_week, last_week, next_month, last_month, next_year, last_year,
    next_weekday, last_weekday, # General weekday finders
    next_monday, last_monday, next_tuesday, last_tuesday, next_wednesday, last_wednesday,
    next_thursday, last_thursday, next_friday, last_friday, next_saturday, last_saturday,
    next_sunday, last_sunday # Specific weekday functions
)

# Formatting functions
from .formatters import to_iso, to_unix_timestamp, to_epoch, format_time, to_rfc2822

# Parsing functions
from .parsers import parse, parse_iso, parse_date

# Check and comparison functions
from .checks import (
    is_today, is_future, is_past, is_weekend, is_weekday, is_leap_year,
    is_same_day, is_same_week, is_same_month, is_same_year
)

# --- Date & Time Constructors ---

def date_of(year: int, month: int, day: int) -> date:
    """
    Creates a new date object.

    Args:
        year (int): The year (e.g., 2025).
        month (int): The month (1-12).
        day (int): The day of the month (1-31).

    Returns:
        date: A new date object.
    """
    return date(year, month, day)

def time_of(hour: int, minute: int = 0, second: int = 0, microsecond: int = 0) -> time:
    """
    Creates a new time object.

    Args:
        hour (int): The hour (0-23).
        minute (int, optional): The minute (0-59). Defaults to 0.
        second (int, optional): The second (0-59). Defaults to 0.
        microsecond (int, optional): The microsecond (0-999999). Defaults to 0.

    Returns:
        time: A new time object.
    """
    return time(hour, minute, second, microsecond)


# --- Public API Export ---
__all__ = [
    "__version__",

    # Core Generators
    "now", "today", "tomorrow", "yesterday",

    # Relative Time
    "next_week", "last_week",
    "next_month", "last_month",
    "next_year", "last_year",
    "next_weekday", "last_weekday",
    "next_monday", "last_monday",
    "next_tuesday", "last_tuesday",
    "next_wednesday", "last_wednesday",
    "next_thursday", "last_thursday",
    "next_friday", "last_friday",
    "next_saturday", "last_saturday",
    "next_sunday", "last_sunday",

    # Delta Helpers
    "days", "hours", "minutes", "seconds", "weeks", "delta",
    "add_months", "add_years", # For precise month/year additions

    # Date & Time Constructors
    "date_of", "time_of",

    # Formatting
    "to_iso", "to_unix_timestamp", "to_epoch", "format_time", "to_rfc2822",

    # Parsing
    "parse", "parse_iso", "parse_date",

    # Timezone Utilities
    "set_default_timezone", "to_timezone", "ensure_aware", "ensure_utc",

    # Checks & Comparisons
    "is_today", "is_future", "is_past", "is_weekend", "is_weekday", "is_leap_year",
    "is_same_day", "is_same_week", "is_same_month", "is_same_year",

    # Constants
    "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY",
]