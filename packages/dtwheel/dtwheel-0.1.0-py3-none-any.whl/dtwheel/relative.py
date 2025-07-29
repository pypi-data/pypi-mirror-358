# dtwheel/relative.py
"""
Provides utilities for calculating dates and datetimes relative to a given base point, including:
  - "now": returns the current datetime (timezone-aware if default set)
  - "today": returns the current date (timezone-aware if default set)
  - next_weekday / last_weekday: find next/previous weekday occurrences
  - next/last week, month, year functions
  - Convenience functions: next_monday, last_friday, etc.

All functions accept either date or datetime, preserving time and tzinfo when returning datetimes.
"""
from datetime import datetime, date, timedelta
from typing import Union, TypeVar

# Weekday constants (MONDAY=0 ... SUNDAY=6)
from .constants import MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
# Helpers to normalize input types
from ._helpers import _convert_to_date, _convert_to_datetime
# Accurate month/year arithmetic
from .deltas import add_months, add_years
# Default timezone for "now()" and "today()"
from .timezone import get_default_timezone

# Generic type for functions returning date or datetime
TDateOrDatetime = TypeVar('TDateOrDatetime', date, datetime)


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
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError # Imported locally to avoid circular dep

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

def tomorrow(from_date: date | datetime = None, tz: str = None) -> date:
    """
    Returns tomorrow's date.

    Args:
        from_date (Union[date, datetime], optional): The base date. Defaults to today().
        tz (str, optional): Timezone context if `from_date` is None.

    Returns:
        date: Tomorrow's date.
    """
    base_date = _convert_to_date(from_date or today(tz))
    return base_date + timedelta(days=1)

def yesterday(from_date: date | datetime = None, tz: str = None) -> date:
    """
    Returns yesterday's date.

    Args:
        from_date (Union[date, datetime], optional): The base date. Defaults to today().
        tz (str, optional): Timezone context if `from_date` is None.

    Returns:
        date: Yesterday's date.
    """
    base_date = _convert_to_date(from_date or today(tz))
    return base_date - timedelta(days=1)


def next_weekday(
    from_date: Union[date, datetime],
    day_of_week: int,
    include_today: bool = False
) -> Union[date, datetime]:
    """
    Return the next occurrence of the specified weekday.

    Args:
        from_date: Starting point (date or datetime).
        day_of_week: Target weekday (0=Monday ... 6=Sunday).
        include_today: If True, return from_date when its weekday matches.

    Returns:
        A date or datetime for the next matching weekday.
        The type of the returned object (date or datetime) matches the input `from_date`.
        If `from_date` is a datetime, its time and timezone information are preserved.
    """
    base_obj = from_date # Keep original object to determine return type and preserve time/tzinfo
    base_date = _convert_to_date(from_date) # Convert to date for weekday calculation

    current_weekday = base_date.weekday()

    if include_today and current_weekday == day_of_week:
        return base_obj # Return original object if matches and include_today is True

    days_until = (day_of_week - current_weekday + 7) % 7
    if days_until == 0:
        days_until = 7 # If current_weekday is the target and include_today is False, go to next week

    result_date = base_date + timedelta(days=days_until)

    if isinstance(base_obj, datetime):
        # Combine the new date with the original time and tzinfo
        return datetime.combine(result_date, base_obj.timetz())
    return result_date


def last_weekday(
    from_date: Union[date, datetime],
    day_of_week: int,
    include_today: bool = False
) -> Union[date, datetime]:
    """
    Return the most recent past occurrence of the specified weekday.

    Args:
        from_date: Starting point (date or datetime).
        day_of_week: Target weekday (0=Monday ... 6=Sunday).
        include_today: If True, return from_date when its weekday matches.

    Returns:
        A date or datetime for the last matching weekday.
        The type of the returned object (date or datetime) matches the input `from_date`.
        If `from_date` is a datetime, its time and timezone information are preserved.
    """
    base_obj = from_date # Keep original object to determine return type and preserve time/tzinfo
    base_date = _convert_to_date(from_date) # Convert to date for weekday calculation

    current_weekday = base_date.weekday()

    if include_today and current_weekday == day_of_week:
        return base_obj # Return original object if matches and include_today is True

    days_since = (current_weekday - day_of_week + 7) % 7
    if days_since == 0:
        days_since = 7 # If current_weekday is the target and include_today is False, go to previous week

    result_date = base_date - timedelta(days=days_since)

    if isinstance(base_obj, datetime):
        # Combine the new date with the original time and tzinfo
        return datetime.combine(result_date, base_obj.timetz())
    return result_date

# -------------------------------------------------------------------------- #
# Relative "next" and "last" intervals: week, month, year
# -------------------------------------------------------------------------- #

def next_week(from_date: Union[date, datetime] = None) -> Union[date, datetime]:
    """
    Return the date/datetime exactly one week after the given date.
    If no date is provided, uses `dtwheel.now()`.
    The return type matches the input type.
    """
    if from_date is None:
        from_date = now() # Use the internal 'now'
    return from_date + timedelta(weeks=1)


def last_week(from_date: Union[date, datetime] = None) -> Union[date, datetime]:
    """
    Return the date/datetime exactly one week before the given date.
    If no date is provided, uses `dtwheel.now()`.
    The return type matches the input type.
    """
    if from_date is None:
        from_date = now() # Use the internal 'now'
    return from_date - timedelta(weeks=1)


def next_month(from_date: Union[date, datetime] = None) -> Union[date, datetime]:
    """
    Return the date/datetime one month after the given date.
    Handles month-end rollovers.
    If no date is provided, uses `dtwheel.now()`.
    The return type matches the input type.
    """
    if from_date is None:
        from_date = now() # Use the internal 'now'
    return add_months(from_date, 1)


def last_month(from_date: Union[date, datetime] = None) -> Union[date, datetime]:
    """
    Return the date/datetime one month before the given date.
    Handles month-end rollovers.
    If no date is provided, uses `dtwheel.now()`.
    The return type matches the input type.
    """
    if from_date is None:
        from_date = now() # Use the internal 'now'
    return add_months(from_date, -1)


def next_year(from_date: Union[date, datetime] = None) -> Union[date, datetime]:
    """
    Return the date/datetime one year after the given date.
    Handles leap years.
    If no date is provided, uses `dtwheel.now()`.
    The return type matches the input type.
    """
    if from_date is None:
        from_date = now() # Use the internal 'now'
    return add_years(from_date, 1)


def last_year(from_date: Union[date, datetime] = None) -> Union[date, datetime]:
    """
    Return the date/datetime one year before the given date.
    Handles leap years.
    If no date is provided, uses `dtwheel.now()`.
    The return type matches the input type.
    """
    if from_date is None:
        from_date = now() # Use the internal 'now'
    return add_years(from_date, -1)

# -------------------------------------------------------------------------- #
# Convenience helpers for specific weekdays
# -------------------------------------------------------------------------- #
# Each helper wraps next_weekday/last_weekday with a fixed constant.

def next_monday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Monday (optional: include today if it's Monday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, MONDAY, include_today)


def last_monday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Monday (optional: include today if it's Monday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, MONDAY, include_today)


def next_tuesday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Tuesday (optional: include today if it's Tuesday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, TUESDAY, include_today)


def last_tuesday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Tuesday (optional: include today if it's Tuesday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, TUESDAY, include_today)


def next_wednesday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Wednesday (optional: include today if it's Wednesday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, WEDNESDAY, include_today)


def last_wednesday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Wednesday (optional: include today if it's Wednesday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, WEDNESDAY, include_today)


def next_thursday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Thursday (optional: include today if it's Thursday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, THURSDAY, include_today)


def last_thursday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Thursday (optional: include today if it's Thursday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, THURSDAY, include_today)


def next_friday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Friday (optional: include today if it's Friday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, FRIDAY, include_today)


def last_friday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Friday (optional: include today if it's Friday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, FRIDAY, include_today)


def next_saturday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Saturday (optional: include today if it's Saturday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, SATURDAY, include_today)


def last_saturday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Saturday (optional: include today if it's Saturday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, SATURDAY, include_today)


def next_sunday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the next Sunday (optional: include today if it's Sunday)."""
    if from_date is None:
        from_date = now()
    return next_weekday(from_date, SUNDAY, include_today)


def last_sunday(from_date: Union[date, datetime] = None, include_today: bool = False) -> Union[date, datetime]:
    """Get the last Sunday (optional: include today if it's Sunday)."""
    if from_date is None:
        from_date = now()
    return last_weekday(from_date, SUNDAY, include_today)
