"""
Path parsing utilities.
"""
from __future__ import annotations
from pathlib import Path, PurePosixPath

def coerce_path(path: str | Path | PurePosixPath) -> PurePosixPath:
    """
    Coerces a string or path object into a relative PurePosixPath.

    Verifies that the path is relative and does not contain wildcards, `~`, or `..`.

    Args:
        path: The path to coerce.

    Returns:
        The coerced relative path.

    Raises:
        ValueError: If the path is absolute, contains wildcards, `~`, or `..`.
    """
    if isinstance(path, (Path, PurePosixPath)):
        if path.is_absolute():
            raise ValueError(f"Path must be relative: {path}")
        result = PurePosixPath(path)
    else:
        result = PurePosixPath(path)
        if result.is_absolute():
            raise ValueError(f"Path must be relative: {path}")

    if any(c in str(result) for c in '*?['):
        raise ValueError(f"Path must not contain wildcards: {path}")

    for part in result.parts:
        if part == '..' or part == '~':
            raise ValueError(f"Path must not contain '{part}': {path}")

    return result

def parse_path(text: str) -> PurePosixPath:
    """
    Parses a virtual path starting with `~/` into a relative PurePosixPath.

    The path must start with `~/`. The resulting path is relative to the
    virtual root. It must not contain wildcards, `~` (except the prefix),
    or `..` components. It cannot be just `.`.

    Args:
        text: The path string to parse.

    Returns:
        The parsed relative path.

    Raises:
        ValueError: If the path format is invalid.
    """
    if not text.startswith('~/'):
        raise ValueError(f"Path must start with ~/: {text}")

    clean_text = text[2:]
    path = PurePosixPath(clean_text)

    if path.is_absolute():
        raise ValueError(f"Path must be relative to project root: {text}")

    if any(c in str(path) for c in '*?['):
        raise ValueError(f"Path must not contain wildcards: {text}")

    for part in path.parts:
        if part == '..' or part == '~':
             raise ValueError(f"Path must not contain '{part}': {text}")

    if path == PurePosixPath('.'):
        raise ValueError(f"Path cannot be the root directory: {text}")

    return path

__all__ = [
    'coerce_path',
    'parse_path',
]
