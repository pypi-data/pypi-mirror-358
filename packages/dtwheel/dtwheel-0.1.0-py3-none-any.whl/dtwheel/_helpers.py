# dtwheel/_helpers.py
"""
Internal utility functions for the dtwheel library.
These functions are not part of the public API and are prefixed with an underscore.
"""

from datetime import datetime, date
from typing import Union, TypeVar

# Define a TypeVar to allow returning the same type as the input (date or datetime)
TDateOrDatetime = TypeVar('TDateOrDatetime', date, datetime)

def _convert_to_datetime(d: Union[date, datetime]) -> datetime:
    """
    Ensures input is a datetime object, converting date if necessary.
    Time component for a date object will be midnight (00:00:00).

    Args:
        d (Union[date, datetime]): The date or datetime object to convert.

    Returns:
        datetime: The converted datetime object.

    Raises:
        TypeError: If the input is not a date or datetime object.
    """
    if isinstance(d, datetime):
        return d
    elif isinstance(d, date):
        # Combine the date with a default time of midnight and no timezone
        return datetime(d.year, d.month, d.day, 0, 0, 0, 0)
    raise TypeError(f"Expected date or datetime object, got {type(d)}")

def _convert_to_date(d: Union[date, datetime]) -> date:
    """
    Ensures input is a date object, converting datetime if necessary.

    Args:
        d (Union[date, datetime]): The date or datetime object to convert.

    Returns:
        date: The converted date object.

    Raises:
        TypeError: If the input is not a date or datetime object.
    """
    if isinstance(d, datetime):
        return d.date()
    elif isinstance(d, date):
        return d
    raise TypeError(f"Expected date or datetime object, got {type(d)}")

def _assert_aware(dt: datetime):
    """
    Asserts that a datetime object is timezone-aware.
    Raises a ValueError if it is naive.
    """
    if dt.tzinfo is None:
        raise ValueError("Datetime object must be timezone-aware for this operation.")
