"""
Path parsing utilities.
"""
from __future__ import annotations
from pathlib import PurePosixPath

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

    # Check for wildcards in string representation
    if any(c in clean_text for c in '*?['):
        raise ValueError(f"Path must not contain wildcards: {text}")

    path = PurePosixPath(clean_text)

    # PurePosixPath collapses '.' but not '..'.
    # If text is "~/", clean_text is "", path is ".".
    # If text is "~/.", clean_text is ".", path is ".".
    if path == PurePosixPath('.'):
        raise ValueError(f"Path cannot be the root directory: {text}")

    # Check for absolute path (should not happen if we strip ~/, unless user does ~//...)
    if path.is_absolute():
        raise ValueError(f"Path must be relative to project root: {text}")

    for part in path.parts:
        if part == '..':
            raise ValueError(f"Path must not contain '..': {text}")
        if part == '~':
            raise ValueError(f"Path must not contain '~': {text}")

    return path

__all__ = [
    'parse_path',
]
