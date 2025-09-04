"""
Filesystem utilities.

This package provides functions for interacting with the filesystem, including
path manipulation, file I/O, and archive handling.

This module provides core filesystem utilities for paths and I/O.

Submodules
----------
archives
    Utilities for handling timestamped file-based archives.
zones
    Zoning system for mapping abstract zone names to filesystem paths.
"""
from pathlib import Path
from llobot.text import normalize_document

def user_home() -> Path:
    return Path.home()

# TODO: Use platform-independent paths (platformdirs package).

def data_home() -> Path:
    return user_home()/'.local/share'

def cache_home() -> Path:
    return user_home()/'.cache'

def create_parents(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def write_bytes(path: Path, data: bytes):
    create_parents(path)
    path.write_bytes(data)

def write_text(path: Path, content: str):
    write_bytes(path, content.encode('utf-8'))

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception as ex:
        raise ValueError(path) from ex

def read_document(path: Path) -> str:
    return normalize_document(read_text(path))

def path_stem(path: Path | str) -> str:
    path = Path(path)
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
