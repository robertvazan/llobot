"""
Utilities for handling timestamped file-based history.

This module provides functions for creating and parsing file paths that
incorporate a timestamp, which is useful for creating histories where files are
named after their creation time.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.utils.time import format_time, parse_time, try_parse_time
from llobot.utils.fs import path_stem

def format_history_filename(time: datetime, suffix: str = '') -> Path:
    """
    Creates a filename from a timestamp and an optional suffix.

    Args:
        time: The timestamp to use for the filename.
        suffix: An optional file suffix (e.g., '.txt').

    Returns:
        A `Path` object representing the filename.
    """
    return Path(format_time(time) + suffix)

def format_history_path(directory: Path | str, time: datetime, suffix: str = '') -> Path:
    """
    Creates a full path for a history file in a given directory.

    Args:
        directory: The directory where the history file will be located.
        time: The timestamp to use for the filename.
        suffix: An optional file suffix.

    Returns:
        A `Path` object for the complete history file path.
    """
    return Path(directory)/format_history_filename(time, suffix)

def parse_history_path(path: Path | str) -> datetime:
    """
    Extracts the timestamp from a history file path.

    The timestamp is expected to be in the filename's stem.

    Args:
        path: The path to the history file.

    Returns:
        The `datetime` object parsed from the filename.

    Raises:
        ValueError: If the filename stem is not a valid timestamp.
    """
    return parse_time(path_stem(path))

def try_parse_history_path(path: Path | str) -> datetime | None:
    """
    Extracts the timestamp from a history file path, returning None on failure.

    Args:
        path: The path to the history file.

    Returns:
        The parsed `datetime` object, or `None` if parsing fails.
    """
    return try_parse_time(path_stem(path))

def iterate_history(directory: Path | str, suffix: str = '') -> Iterable[Path]:
    """
    Iterates over all valid history file paths in a directory.

    A path is considered a valid history file path if its stem can be parsed
    as a timestamp and it has the correct suffix.

    Args:
        directory: The directory to scan for history files.
        suffix: The file suffix to match.

    Returns:
        An iterable of `Path` objects for valid history files.
    """
    directory = Path(directory)
    if not directory.exists():
        return iter(())
    for path in directory.iterdir():
        if path.name.endswith(suffix) and try_parse_time(path.name.removesuffix(suffix)):
            yield path

def recent_history_paths(directory: Path | str, suffix: str = '', cutoff: datetime | None = None) -> Iterable[Path]:
    """
    Iterates over recent history file paths in a directory, from newest to oldest.

    Args:
        directory: The directory to scan.
        suffix: The file suffix to look for.
        cutoff: If provided, only paths with timestamps at or before the cutoff are returned.

    Returns:
        An iterable of paths, sorted descending by time.
    """
    for path in sorted(iterate_history(directory, suffix), reverse=True):
        if cutoff is None or parse_history_path(path) <= cutoff:
            yield path

def last_history_path(directory: Path | str, suffix: str = '', cutoff: datetime | None = None) -> Path | None:
    """
    Finds the most recent history file path in a directory.

    Args:
        directory: The directory to scan.
        suffix: The file suffix to look for.
        cutoff: If provided, only paths with timestamps at or before the cutoff are considered.

    Returns:
        The path to the most recent history file, or None if none are found.
    """
    return next(recent_history_paths(directory, suffix, cutoff), None)

__all__ = [
    'format_history_filename',
    'format_history_path',
    'parse_history_path',
    'try_parse_history_path',
    'iterate_history',
    'recent_history_paths',
    'last_history_path',
]
