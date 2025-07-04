from datetime import datetime, UTC

# Timestamps are optimized for readability at the cost of resolution. We support only timestamps with second precision.
# That is plenty for user interactions. If the user ever happens to perform two actions at the same time, it is okay if only one persists.
# We could expand precision in the future to milliseconds or microseconds if we ever have to support fast ingestion batches.
# We could also artificially ensure uniqueness by incrementing the timestamp beyond current time to prevent duplicates.
# To prevent contaminating everything with the higher precision, we could enable it lazily when duplicates are detected.

def now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)

# We want compact, yet readable format. Single dash between date and time is sufficient for that purpose.

def format(time: datetime) -> str:
    return time.strftime('%Y%m%d-%H%M%S')

def parse(formatted: str) -> datetime:
    return datetime.strptime(formatted, '%Y%m%d-%H%M%S').replace(tzinfo=UTC)

def try_parse(formatted: str) -> datetime | None:
    try:
        return parse(formatted)
    except ValueError:
        return None

__all__ = [
    'now',
    'format',
    'parse',
    'try_parse',
]

