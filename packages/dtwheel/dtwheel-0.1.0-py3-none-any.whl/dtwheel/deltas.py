# dtwheel/deltas.py
"""
Time delta helper functions for dtwheel.
Provides convenient ways to create timedelta objects and handles
approximate month/year additions.
"""

from datetime import datetime, date, timedelta
from typing import Union
import calendar
from ._helpers import _convert_to_date # Import _convert_to_date for robust type handling

# --- Basic Timedelta Helpers ---

def days(n: int) -> timedelta:
    """Returns a timedelta object representing `n` days."""
    return timedelta(days=n)

def hours(n: int) -> timedelta:
    """Returns a timedelta object representing `n` hours."""
    return timedelta(hours=n)

def minutes(n: int) -> timedelta:
    """Returns a timedelta object representing `n` minutes."""
    return timedelta(minutes=n)

def seconds(n: int) -> timedelta:
    """Returns a timedelta object representing `n` seconds."""
    return timedelta(seconds=n)

def weeks(n: int) -> timedelta:
    """Returns a timedelta object representing `n` weeks."""
    return timedelta(weeks=n)

def delta(**kwargs) -> timedelta:
    """
    Creates a timedelta object from keyword arguments.
    Example: dtwheel.delta(days=5, hours=3)

    Args:
        **kwargs: Keyword arguments accepted by datetime.timedelta (e.g., days, seconds, microseconds,
                  milliseconds, minutes, hours, weeks).

    Returns:
        timedelta: A timedelta object.
    """
    return timedelta(**kwargs)

# --- Approximate Month/Year Additions (cannot return timedelta) ---

def _add_months_internal(dt_obj: Union[date, datetime], months_to_add: int) -> Union[date, datetime]:
    """
    Internal helper for adding months, handling date/datetime types and day rollovers.
    This function expects `dt_obj` to be a valid date or datetime object,
    ensuring type consistency at the entry point of the internal logic.
    """
    # Use _convert_to_date to ensure dt_obj is a date for calendar calculations,
    # and _convert_to_date will raise TypeError if dt_obj is not date/datetime.
    is_datetime_input = isinstance(dt_obj, datetime)
    current_date = _convert_to_date(dt_obj)

    # Calculate new month and year
    new_month_total = current_date.month + months_to_add
    new_year = current_date.year + (new_month_total - 1) // 12
    new_month = (new_month_total - 1) % 12 + 1

    # Get the last day of the new month to handle day rollovers (e.g., Jan 31 + 1 month -> Feb 28/29)
    _, last_day_of_new_month = calendar.monthrange(new_year, new_month)
    new_day = min(current_date.day, last_day_of_new_month)

    result_date = date(new_year, new_month, new_day)

    if is_datetime_input:
        # Preserve original time and timezone info
        return datetime.combine(result_date, dt_obj.timetz())
    return result_date

def add_months(dt: Union[date, datetime], n: int) -> Union[date, datetime]:
    """
    Adds `n` months to a given date or datetime object.
    This operation intelligently handles month-end rollovers (e.g., adding 1 month to Jan 31
    will result in Feb 28/29, not March 2).

    Args:
        dt (Union[date, datetime]): The base date or datetime object.
        n (int): The number of months to add (can be negative for subtraction).

    Returns:
        Union[date, datetime]: A new date or datetime object with months added.
    """
    # The type checking for `dt` is now handled within `_add_months_internal` via `_convert_to_date`.
    return _add_months_internal(dt, n)

def add_years(dt: Union[date, datetime], n: int) -> Union[date, datetime]:
    """
    Adds `n` years to a given date or datetime object.
    This operation accounts for leap years and handles day rollovers for February 29th.

    Args:
        dt (Union[date, datetime]): The base date or datetime object.
        n (int): The number of years to add (can be negative for subtraction).

    Returns:
        Union[date, datetime]: A new date or datetime object with years added.
    """
    # The type checking for `dt` is now handled within `_add_months_internal` via `_convert_to_date`.
    # Adding years can be treated as adding 12 * n months
    return _add_months_internal(dt, n * 12)



