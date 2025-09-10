"""
Utilities for handling timestamped file-based archives.

This module provides functions for creating and parsing file paths that
incorporate a timestamp, which is useful for creating archives where files are
named after their creation time.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.utils.time import format_time, parse_time, try_parse_time
from llobot.utils.fs import path_stem

def format_archive_filename(time: datetime, suffix: str = '') -> Path:
    """
    Creates a filename from a timestamp and an optional suffix.

    Args:
        time: The timestamp to use for the filename.
        suffix: An optional file suffix (e.g., '.tar.gz').

    Returns:
        A `Path` object representing the filename.
    """
    return Path(format_time(time) + suffix)

def format_archive_path(directory: Path | str, time: datetime, suffix: str = '') -> Path:
    """
    Creates a full path for an archive file in a given directory.

    Args:
        directory: The directory where the archive file will be located.
        time: The timestamp to use for the filename.
        suffix: An optional file suffix.

    Returns:
        A `Path` object for the complete archive file path.
    """
    return Path(directory)/format_archive_filename(time, suffix)

def parse_archive_path(path: Path | str) -> datetime:
    """
    Extracts the timestamp from an archive path.

    The timestamp is expected to be in the filename's stem.

    Args:
        path: The path to the archive file.

    Returns:
        The `datetime` object parsed from the filename.

    Raises:
        ValueError: If the filename stem is not a valid timestamp.
    """
    return parse_time(path_stem(path))

def try_parse_archive_path(path: Path | str) -> datetime | None:
    """
    Extracts the timestamp from an archive path, returning None on failure.

    Args:
        path: The path to the archive file.

    Returns:
        The parsed `datetime` object, or `None` if parsing fails.
    """
    return try_parse_time(path_stem(path))

def iterate_archive(directory: Path | str, suffix: str = '') -> Iterable[Path]:
    """
    Iterates over all valid archive paths in a directory.

    A path is considered a valid archive path if its stem can be parsed
    as a timestamp and it has the correct suffix.

    Args:
        directory: The directory to scan for archive files.
        suffix: The file suffix to match.

    Returns:
        An iterable of `Path` objects for valid archive files.
    """
    directory = Path(directory)
    if not directory.exists():
        return iter(())
    for path in directory.iterdir():
        if path.name.endswith(suffix) and try_parse_time(path.name.removesuffix(suffix)):
            yield path

def recent_archive_paths(directory: Path | str, suffix: str = '', cutoff: datetime | None = None) -> Iterable[Path]:
    """
    Iterates over recent archive paths in a directory, from newest to oldest.

    Args:
        directory: The directory to scan.
        suffix: The file suffix to look for.
        cutoff: If provided, only paths with timestamps at or before the cutoff are returned.

    Returns:
        An iterable of paths, sorted descending by time.
    """
    for path in sorted(iterate_archive(directory, suffix), reverse=True):
        if cutoff is None or parse_archive_path(path) <= cutoff:
            yield path

def last_archive_path(directory: Path | str, suffix: str = '', cutoff: datetime | None = None) -> Path | None:
    """
    Finds the most recent archive path in a directory.

    Args:
        directory: The directory to scan.
        suffix: The file suffix to look for.
        cutoff: If provided, only paths with timestamps at or before the cutoff are considered.

    Returns:
        The path to the most recent archive file, or None if none are found.
    """
    return next(recent_archive_paths(directory, suffix, cutoff), None)

__all__ = [
    'format_archive_filename',
    'format_archive_path',
    'parse_archive_path',
    'try_parse_archive_path',
    'iterate_archive',
    'recent_archive_paths',
    'last_archive_path',
]
