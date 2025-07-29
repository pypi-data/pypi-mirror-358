# dtwheel/parsers.py
"""
Functions for parsing date and datetime strings into objects.
"""

from datetime import datetime, date, timezone
from typing import Optional, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .constants import COMMON_DATETIME_FORMATS, COMMON_DATE_FORMATS
from .timezone import get_default_timezone, ensure_aware, to_timezone # For timezone awareness and conversion

def parse(date_string: str, format_string: Optional[str] = None,
          tz: Optional[str] = None, make_aware: bool = False) -> datetime:
    """
    Parses a date/datetime string into a datetime object.

    If `format_string` is provided, it attempts to parse using that specific format.
    Otherwise, it attempts to parse using a list of common, well-known formats.

    Args:
        date_string (str): The string to parse.
        format_string (str, optional): The explicit format string (e.g., "%Y-%m-%d %H:%M:%S").
                                       If None, common formats are tried.
        tz (str, optional): Timezone string to apply if the parsed datetime is naive,
                            or to convert to if make_aware is True and the string
                            already contained a different timezone.
        make_aware (bool): If True, ensures the returned datetime is timezone-aware.
                           If the string contains timezone info, it's used. If not,
                           `tz` or the default timezone is applied.

    Returns:
        datetime: The parsed datetime object.

    Raises:
        ValueError: If the string cannot be parsed with the given format or any common formats,
                    or if make_aware is true but no timezone can be determined.
    """
    dt_obj: datetime
    if format_string:
        try:
            dt_obj = datetime.strptime(date_string, format_string)
        except ValueError:
            raise ValueError(f"String '{date_string}' does not match format '{format_string}'")
    else:
        # Try common datetime formats first
        for fmt in COMMON_DATETIME_FORMATS:
            try:
                dt_obj = datetime.strptime(date_string, fmt)
                break
            except ValueError:
                continue
        else:
            # If no datetime format matches, try common date formats and convert to datetime
            for fmt in COMMON_DATE_FORMATS:
                try:
                    parsed_date_obj = datetime.strptime(date_string, fmt).date()
                    # Convert to datetime at midnight if parsed as a date
                    dt_obj = datetime(parsed_date_obj.year, parsed_date_obj.month, parsed_date_obj.day)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Could not parse '{date_string}' with any common formats. "
                                 "Please provide an explicit format_string.")

    if make_aware:
        if dt_obj.tzinfo is None: # If the parsed object is naive
            target_tz_obj = None
            if tz:
                try:
                    target_tz_obj = ZoneInfo(tz)
                except ZoneInfoNotFoundError:
                    raise ValueError(f"Invalid timezone string provided for parsing: '{tz}'")
            else:
                target_tz_obj = get_default_timezone()

            if target_tz_obj:
                dt_obj = dt_obj.replace(tzinfo=target_tz_obj)
            else:
                raise ValueError("Cannot make datetime aware: no timezone provided and default not set/determinable.")
        elif tz: # If dt_obj already has tzinfo and a target tz is provided, convert
            try:
                target_tz_obj = ZoneInfo(tz)
            except ZoneInfoNotFoundError:
                raise ValueError(f"Invalid timezone string provided for parsing: '{tz}'")

            if dt_obj.tzinfo != target_tz_obj:
                 dt_obj = dt_obj.astimezone(target_tz_obj)

    return dt_obj

def parse_iso(iso_string: str, tz: Optional[str] = None, make_aware: bool = True) -> datetime:
    """
    Parses an ISO 8601 formatted datetime string.

    Args:
        iso_string (str): The ISO 8601 string to parse (e.g., "2025-06-26T14:30:00Z").
                          Supports various ISO 8601 formats including with/without milliseconds,
                          and with/without timezone offsets.
        tz (str, optional): Timezone string to apply if the parsed datetime is naive and make_aware is True,
                            or to convert to if the string has a different timezone.
        make_aware (bool): If True, ensures the returned datetime is timezone-aware.

    Returns:
        datetime: The parsed datetime object.

    Raises:
        ValueError: If the string is not a valid ISO 8601 format or if make_aware is true but no timezone can be determined.
    """
    try:
        # datetime.fromisoformat() handles a good range of ISO 8601
        dt_obj = datetime.fromisoformat(iso_string)
    except ValueError:
        # Manual fallback for 'Z' if fromisoformat doesn't handle it perfectly or needs more specific parsing
        if iso_string.endswith('Z'):
            try:
                dt_obj = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                try:
                    dt_obj = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                except ValueError:
                    raise ValueError(f"Could not parse ISO 8601 string: '{iso_string}'")
        else:
            raise ValueError(f"Could not parse ISO 8601 string: '{iso_string}'")

    if make_aware:
        if dt_obj.tzinfo is None: # If the parsed object is naive
            target_tz_obj = None
            if tz:
                try:
                    target_tz_obj = ZoneInfo(tz)
                except ZoneInfoNotFoundError:
                    raise ValueError(f"Invalid timezone string provided for ISO parsing: '{tz}'")
            else:
                target_tz_obj = get_default_timezone()

            if target_tz_obj:
                dt_obj = dt_obj.replace(tzinfo=target_tz_obj)
            else:
                raise ValueError("Cannot make datetime aware: no timezone provided for ISO parsing and default not set/determinable.")
        elif tz: # If already aware, convert if different target tz is specified
            try:
                target_tz_obj = ZoneInfo(tz)
            except ZoneInfoNotFoundError:
                raise ValueError(f"Invalid timezone string provided for ISO parsing: '{tz}'")

            if dt_obj.tzinfo != target_tz_obj:
                dt_obj = dt_obj.astimezone(target_tz_obj)

    return dt_obj

def parse_date(date_string: str, format_string: Optional[str] = None) -> date:
    """
    Parses a date string into a date object.

    If `format_string` is provided, it attempts to parse using that specific format.
    Otherwise, it attempts to parse using a list of common date formats.

    Args:
        date_string (str): The string to parse.
        format_string (str, optional): The explicit format string (e.g., "%Y-%m-%d").
                                       If None, common date formats are tried.

    Returns:
        date: The parsed date object.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    if format_string:
        try:
            return datetime.strptime(date_string, format_string).date()
        except ValueError:
            raise ValueError(f"String '{date_string}' does not match format '{format_string}'")
    else:
        for fmt in COMMON_DATE_FORMATS:
            try:
                return datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Could not parse '{date_string}' with any common date formats. "
                         "Please provide an explicit format_string.")
