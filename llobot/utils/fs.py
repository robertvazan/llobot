"""
Filesystem utilities.

This module provides functions for interactions with the filesystem, including
path manipulation, file I/O, and path component extraction.
"""
import re
from pathlib import Path, PurePosixPath
from llobot.utils.text import normalize_document

def user_home() -> Path:
    """Gets the user's home directory."""
    return Path.home()

# TODO: Use platform-independent paths (platformdirs package).

def data_home() -> Path:
    """Gets the user's data directory."""
    return user_home()/'.local/share'

def cache_home() -> Path:
    """Gets the user's cache directory."""
    return user_home()/'.cache'

def create_parents(path: Path):
    """
    Ensures that the parent directory of a path exists.

    Args:
        path: The path whose parent directory should be created.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

def write_bytes(path: Path, data: bytes):
    """
    Writes bytes to a file, creating parent directories if necessary.

    Args:
        path: The path to the file to write.
        data: The bytes to write to the file.
    """
    create_parents(path)
    path.write_bytes(data)

def write_text(path: Path, content: str):
    """
    Writes text to a file, creating parent directories if necessary.

    The text is encoded as UTF-8.

    Args:
        path: The path to the file to write.
        content: The string content to write.
    """
    write_bytes(path, content.encode('utf-8'))

_CONTROL_CHARS_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

def read_text(path: Path) -> str:
    """
    Reads text from a file.

    It enforces strict UTF-8 decoding and rejects files with control characters
    other than TAB, LF, and CR. It also normalizes newlines to LF.

    Args:
        path: The path to the file to read.

    Returns:
        The content of the file as a string.

    Raises:
        ValueError: If the file cannot be read, is not valid UTF-8, or contains
                    forbidden control characters.
    """
    try:
        # read_text() uses open() which defaults to universal newlines mode,
        # so it translates \r\n and \r to \n.
        content = path.read_text(encoding='utf-8', errors='strict')
    except Exception as ex:
        raise ValueError(f"Failed to read {path}: {ex}") from ex

    if _CONTROL_CHARS_RE.search(content):
        raise ValueError(f"Control characters found in {path}")

    return content

def read_document(path: Path) -> str:
    """
    Reads and normalizes a document from a file.

    This function reads a text file and then normalizes its content using
    `normalize_document`.

    Args:
        path: The path to the document to read.

    Returns:
        The normalized content of the document.
    """
    return normalize_document(read_text(path))

def path_stem(path: Path | PurePosixPath | str) -> str:
    """
    Gets the stem of a path, removing all extensions.

    Unlike `pathlib.Path.stem`, this function removes all suffixes,
    not just the last one. For example, for "archive.tar.gz", it returns
    "archive", while `Path.stem` would return "archive.tar".

    Args:
        path: The path or path string.

    Returns:
        The stem of the path.
    """
    path = PurePosixPath(path)
    while path.suffix:
        path = path.with_suffix('')
    return path.name

__all__ = [
    'user_home',
    'data_home',
    'cache_home',
    'create_parents',
    'write_bytes',
    'write_text',
    'read_text',
    'read_document',
    'path_stem',
]
