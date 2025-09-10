"""
Utilities for handling timestamps.

Timestamps are optimized for readability at the cost of resolution. We support
only timestamps with second precision. That is plenty for user interactions.
If the user ever happens to perform two actions at the same time, it is okay
if only one persists.

We could expand precision in the future to milliseconds or microseconds if we
ever have to support fast ingestion batches. We could also artificially ensure
uniqueness by incrementing the timestamp beyond current time to prevent
duplicates. To prevent contaminating everything with the higher precision, we
could enable it lazily when duplicates are detected.

The string format is `YYYYMMDD-HHMMSS`, which is compact yet readable.
"""
from datetime import datetime, UTC

def current_time() -> datetime:
    """
    Gets the current time in UTC, with microsecond precision removed.

    Returns:
        A `datetime` object for the current time.
    """
    return datetime.now(UTC).replace(microsecond=0)

def format_time(time: datetime) -> str:
    """
    Formats a datetime object into a compact, readable string.

    The format is `YYYYMMDD-HHMMSS`.

    Args:
        time: The `datetime` object to format.

    Returns:
        The formatted timestamp string.
    """
    return time.strftime('%Y%m%d-%H%M%S')

def parse_time(formatted: str) -> datetime:
    """
    Parses a timestamp string into a UTC datetime object.

    The expected format is `YYYYMMDD-HHMMSS`.

    Args:
        formatted: The timestamp string to parse.

    Returns:
        The parsed `datetime` object, with UTC timezone.

    Raises:
        ValueError: If the string is not in the correct format.
    """
    return datetime.strptime(formatted, '%Y%m%d-%H%M%S').replace(tzinfo=UTC)

def try_parse_time(formatted: str) -> datetime | None:
    """
    Tries to parse a timestamp string, returning None on failure.

    The expected format is `YYYYMMDD-HHMMSS`.

    Args:
        formatted: The timestamp string to parse.

    Returns:
        The parsed `datetime` object, or `None` if parsing fails.
    """
    try:
        return parse_time(formatted)
    except ValueError:
        return None

__all__ = [
    'current_time',
    'format_time',
    'parse_time',
    'try_parse_time',
]
