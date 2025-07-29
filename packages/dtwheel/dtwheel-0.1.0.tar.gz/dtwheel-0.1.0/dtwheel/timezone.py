# dtwheel/timezone.py
"""
Timezone handling logic for the dtwheel library.
Manages the default timezone and provides conversion utilities.
"""

import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError # Python 3.9+
from ._helpers import _assert_aware # Import _assert_aware helper

# Internal variable to store the default timezone, initially None
_DEFAULT_TIMEZONE = None

def set_default_timezone(tz_str: str):
    """
    Sets the default timezone for dtwheel operations.
    All operations that do not explicitly specify a timezone will use this.

    Args:
        tz_str (str): The string name of the timezone (e.g., 'UTC', 'America/New_York').

    Raises:
        ValueError: If the provided timezone string is invalid.
    """
    global _DEFAULT_TIMEZONE
    try:
        _DEFAULT_TIMEZONE = ZoneInfo(tz_str)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone string: '{tz_str}'")

def get_default_timezone() -> ZoneInfo | None:
    """
    Retrieves the currently set default timezone. If not explicitly set,
    it attempts to determine the system's local timezone.

    Returns:
        ZoneInfo | None: The default timezone, or None if it cannot be determined
                         and hasn't been set, in which case naive datetimes are returned.
    """
    global _DEFAULT_TIMEZONE
    if _DEFAULT_TIMEZONE is None:
        try:
            # Attempt to get the system's local timezone (Python 3.9+)
            _DEFAULT_TIMEZONE = ZoneInfo.system()
        except ZoneInfoNotFoundError:
            # Fallback to UTC if system timezone cannot be determined or found.
            # A user can override this with set_default_timezone().
            _DEFAULT_TIMEZONE = ZoneInfo("UTC")
        except Exception:
            # Catch other potential errors (e.g., if zoneinfo data is missing)
            _DEFAULT_TIMEZONE = None # Explicitly set to None for truly naive fallback
            # In a real library, you might want to log this warning:
            # import warnings
            # warnings.warn("Could not determine system timezone. Using naive datetimes by default. Use set_default_timezone() for explicit timezone handling.")
    return _DEFAULT_TIMEZONE

def to_timezone(dt_obj: datetime, tz_str: str) -> datetime:
    """
    Converts a timezone-aware datetime object to a new timezone.

    Args:
        dt_obj (datetime): The timezone-aware datetime object to convert.
        tz_str (str): The target timezone string (e.g., 'America/New_York').

    Returns:
        datetime: A new datetime object in the target timezone.

    Raises:
        ValueError: If the input datetime object is naive or the timezone string is invalid.
    """
    _assert_aware(dt_obj) # Using the helper function here
    try:
        target_tz = ZoneInfo(tz_str)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone string: '{tz_str}'")

    return dt_obj.astimezone(target_tz)

def ensure_aware(dt_obj: datetime, default_tz: ZoneInfo = None) -> datetime:
    """
    Ensures a datetime object is timezone-aware. If it's naive, it attaches
    the provided default_tz or the library's default timezone.

    Args:
        dt_obj (datetime): The datetime object.
        default_tz (ZoneInfo, optional): The timezone to apply if dt_obj is naive.
                                         Defaults to the library's default timezone.

    Returns:
        datetime: A timezone-aware datetime object.
    """
    if dt_obj.tzinfo is None:
        tz_to_apply = default_tz or get_default_timezone()
        if tz_to_apply is None:
            raise ValueError("No default timezone set or determinable to make datetime aware.")
        return dt_obj.replace(tzinfo=tz_to_apply)
    return dt_obj

def ensure_utc(dt_obj: datetime) -> datetime:
    """
    Ensures a datetime object is in UTC. If naive, it assumes UTC.
    If aware, it converts to UTC.

    Args:
        dt_obj (datetime): The datetime object.

    Returns:
        datetime: A new datetime object representing the same point in time, but in UTC.
    """
    if dt_obj.tzinfo is None:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(timezone.utc)
