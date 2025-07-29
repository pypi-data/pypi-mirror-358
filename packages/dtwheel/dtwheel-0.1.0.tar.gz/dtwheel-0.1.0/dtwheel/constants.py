# dtwheel/constants.py
"""
Constants used throughout the dtwheel library.
"""

import calendar

# Weekday constants (matching datetime.weekday() where Monday is 0 and Sunday is 6)
MONDAY = calendar.MONDAY
TUESDAY = calendar.TUESDAY
WEDNESDAY = calendar.WEDNESDAY
THURSDAY = calendar.THURSDAY
FRIDAY = calendar.FRIDAY
SATURDAY = calendar.SATURDAY
SUNDAY = calendar.SUNDAY

# Common date and time formats for parsing and formatting
ISO_8601_FORMAT = "%Y-%m-%dT%H:%M:%S"
ISO_8601_Z_FORMAT = "%Y-%m-%dT%H:%M:%SZ" # For UTC
ISO_8601_MICROSECOND_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
RFC_2822_FORMAT = "%a, %d %b %Y %H:%M:%S %z" # e.g., "Wed, 25 Jun 2025 21:52:31 +0530"

# List of common formats to attempt parsing if no format string is provided
COMMON_DATETIME_FORMATS = [
    ISO_8601_MICROSECOND_FORMAT,
    ISO_8601_FORMAT,
    ISO_8601_Z_FORMAT,
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
    RFC_2822_FORMAT,
]

COMMON_DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%b %d, %Y", # e.g., Jun 25, 2025
]
