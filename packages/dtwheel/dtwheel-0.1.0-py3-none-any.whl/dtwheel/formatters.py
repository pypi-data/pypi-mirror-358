# dtwheel/formatters.py
"""
Formatting functions for the dtwheel library.
Provides convenient ways to convert datetime objects to various string formats.
"""

from datetime import datetime, date, timezone
from typing import Union
from zoneinfo import ZoneInfo # Used for type hinting ZoneInfo objects
from ._helpers import _assert_aware # Import _assert_aware helper
from .constants import RFC_2822_FORMAT # Import common formats
from .timezone import ensure_aware, ensure_utc # Import from timezone module to avoid circular dependency

def to_iso(dt_obj: Union[date, datetime]) -> str:
    """
    Converts a date or datetime object to ISO 8601 format.
    For datetime objects, if timezone-aware, the offset is included.

    Args:
        dt_obj (Union[date, datetime]): The date or datetime object.

    Returns:
        str: The ISO 8601 formatted string.
    """
    if isinstance(dt_obj, datetime):
        # Ensure it's aware if possible, then format. isoformat() handles offsets correctly.
        return ensure_aware(dt_obj).isoformat()
    return dt_obj.isoformat()

def to_unix_timestamp(dt_obj: datetime) -> float:
    """
    Converts a datetime object to a Unix timestamp (seconds since epoch) as a float.
    The datetime object is first converted to UTC for a consistent epoch.

    Args:
        dt_obj (datetime): The datetime object.

    Returns:
        float: The Unix timestamp.
    """
    # Ensure UTC for a consistent epoch timestamp
    return ensure_utc(dt_obj).timestamp()

def to_epoch(dt_obj: datetime) -> float:
    """
    Alias for to_unix_timestamp. Converts a datetime object to epoch time (seconds since epoch) as a float.
    Ensures UTC conversion.

    Args:
        dt_obj (datetime): The datetime object.

    Returns:
        float: The epoch time.
    """
    return to_unix_timestamp(dt_obj)

def format_time(dt_obj: Union[date, datetime], fmt: str) -> str:
    """
    Formats a date or datetime object using a custom format string (strftime).
    If the dt_obj is a datetime and is naive, it attempts to make it aware
    using the default timezone before formatting if the format string includes
    timezone information (%z or %Z).

    Args:
        dt_obj (Union[date, datetime]): The date or datetime object.
        fmt (str): The format string (e.g., "%Y-%m-%d %H:%M:%S").

    Returns:
        str: The formatted string.
    """
    if isinstance(dt_obj, datetime):
        # If format string requires timezone info and dt_obj is naive, try to make it aware
        if ('%z' in fmt or '%Z' in fmt) and dt_obj.tzinfo is None:
            return ensure_aware(dt_obj).strftime(fmt)
        return dt_obj.strftime(fmt)
    return dt_obj.strftime(fmt)

def to_rfc2822(dt_obj: datetime) -> str:
    """
    Formats a datetime object as an RFC 2822 string.
    Ensures the datetime is timezone-aware. If naive, it will attempt to make it aware
    using the default timezone. Raises ValueError if no timezone can be determined.

    Args:
        dt_obj (datetime): The datetime object.

    Returns:
        str: The RFC 2822 formatted string (e.g., "Wed, 25 Jun 2025 21:52:31 +0530").

    Raises:
        ValueError: If the datetime is naive and no default timezone can be determined.
    """
    # RFC 2822 requires timezone info. Ensure awareness first.
    aware_dt = ensure_aware(dt_obj)
    if aware_dt.tzinfo is None:
        # This case should ideally be caught by ensure_aware, but as a safeguard
        raise ValueError("Cannot format naive datetime to RFC 2822 without a timezone.")
    return aware_dt.strftime(RFC_2822_FORMAT)
