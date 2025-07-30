"""Common utilities for model classes."""

from datetime import datetime, timezone


def parse_datetime(date_str: str | None) -> datetime | None:
    """Parse ISO format datetime string to datetime object with UTC timezone.

    Args:
        date_str (str | None): ISO format datetime string or None

    Returns:
        datetime | None: Parsed datetime with UTC timezone or None if input is None
    """
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)