# dtwheel/checks.py
"""
Functions for checking properties and performing comparisons of date and datetime objects.
"""
from datetime import datetime, date, timedelta
from typing import Union
import calendar

from ._helpers import _convert_to_date # _convert_to_datetime is imported in _helpers but not directly used here
# Import now from .relative to avoid circular dependency with __init__ and timezone
from .relative import now # For is_today, is_future, is_past
from .constants import SATURDAY, SUNDAY # For is_weekend

def is_today(dt: Union[date, datetime]) -> bool:
    """
    Checks if the given date or datetime object falls on today's date (current local day).

    Args:
        dt (Union[datetime.date, datetime.datetime]): The date or datetime object to check.

    Returns:
        bool: True if the date matches today's date, False otherwise.
    """
    return _convert_to_date(dt) == now().date()

def is_future(dt: datetime, relative_to: datetime = None) -> bool:
    """
    Checks if the given datetime.datetime object is in the future.
    Comparison is made against dtwheel.now() by default, or relative_to if provided.
    Requires consistent timezone awareness for comparison.

    Args:
        dt (datetime.datetime): The datetime object to check.
        relative_to (datetime.datetime, optional): The datetime object to compare against. Defaults to dtwheel.now().

    Returns:
        bool: True if dt is in the future relative to the comparison point, False otherwise.

    Raises:
        ValueError: If comparing aware and naive datetimes.
    """
    compare_to = relative_to if relative_to is not None else now()

    # Check for consistent timezone awareness
    if (dt.tzinfo is not None and compare_to.tzinfo is None) or \
       (dt.tzinfo is None and compare_to.tzinfo is not None):
        raise ValueError("Cannot compare timezone-aware and naive datetimes directly.")

    return dt > compare_to

def is_past(dt: datetime, relative_to: datetime = None) -> bool:
    """
    Checks if the given datetime.datetime object is in the past.
    Comparison is made against dtwheel.now() by default, or relative_to if provided.
    Requires consistent timezone awareness for comparison.

    Args:
        dt (datetime.datetime): The datetime object to check.
        relative_to (datetime.datetime, optional): The datetime object to compare against. Defaults to dtwheel.now().

    Returns:
        bool: True if dt is in the past relative to the comparison point, False otherwise.

    Raises:
        ValueError: If comparing aware and naive datetimes.
    """
    compare_to = relative_to if relative_to is not None else now()

    # Check for consistent timezone awareness
    if (dt.tzinfo is not None and compare_to.tzinfo is None) or \
       (dt.tzinfo is None and compare_to.tzinfo is not None):
        raise ValueError("Cannot compare timezone-aware and naive datetimes directly.")

    return dt < compare_to

def is_weekend(dt: Union[date, datetime]) -> bool:
    """
    Checks if the given date or datetime object falls on a Saturday or Sunday.

    Args:
        dt (Union[datetime.date, datetime.datetime]): The date or datetime object to check.

    Returns:
        bool: True if it's a weekend, False otherwise.
    """
    weekday = _convert_to_date(dt).weekday()
    return weekday == SATURDAY or weekday == SUNDAY

def is_weekday(dt: Union[date, datetime]) -> bool:
    """
    Checks if the given date or datetime object falls on a weekday (Monday to Friday).

    Args:
        dt (Union[datetime.date, datetime.datetime]): The date or datetime object to check.

    Returns:
        bool: True if it's a weekday, False otherwise.
    """
    return not is_weekend(dt)

def is_leap_year(year: int) -> bool:
    """
    Checks if the given year is a leap year.

    Args:
        year (int): The year to check.

    Returns:
        bool: True if it's a leap year, False otherwise.
    """
    return calendar.isleap(year)

def is_same_day(dt1: Union[date, datetime], dt2: Union[date, datetime]) -> bool:
    """
    Checks if two date/datetime objects represent the same calendar day.

    Args:
        dt1 (Union[datetime.date, datetime.datetime]): The first object.
        dt2 (Union[datetime.date, datetime.datetime]): The second object.

    Returns:
        bool: True if they are on the same calendar day, False otherwise.
    """
    return _convert_to_date(dt1) == _convert_to_date(dt2)

def is_same_week(dt1: Union[date, datetime], dt2: Union[date, datetime]) -> bool:
    """
    Checks if two date/datetime objects fall within the same calendar week (assuming Monday as the start of the week).

    Args:
        dt1 (Union[datetime.date, datetime.datetime]): The first object.
        dt2 (Union[datetime.date, datetime.datetime]): The second object.

    Returns:
        bool: True if they are in the same calendar week, False otherwise.
    """
    # Get the Monday of the week for both dates
    monday1 = _convert_to_date(dt1) - timedelta(days=_convert_to_date(dt1).weekday())
    monday2 = _convert_to_date(dt2) - timedelta(days=_convert_to_date(dt2).weekday())
    return monday1 == monday2

def is_same_month(dt1: Union[date, datetime], dt2: Union[date, datetime]) -> bool:
    """
    Checks if two date/datetime objects fall within the same calendar month and year.

    Args:
        dt1 (Union[datetime.date, datetime.datetime]): The first object.
        dt2 (Union[datetime.date, datetime.datetime]): The second object.

    Returns:
        bool: True if they are in the same calendar month and year, False otherwise.
    """
    d1 = _convert_to_date(dt1)
    d2 = _convert_to_date(dt2)
    return d1.year == d2.year and d1.month == d2.month

def is_same_year(dt1: Union[date, datetime], dt2: Union[date, datetime]) -> bool:
    """
    Checks if two date/datetime objects fall within the same calendar year.

    Args:
        dt1 (Union[datetime.date, datetime.datetime]): The first object.
        dt2 (Union[datetime.date, datetime.datetime]): The second object.

    Returns:
        bool: True if they are in the same calendar year, False otherwise.
    """
    return _convert_to_date(dt1).year == _convert_to_date(dt2).year
