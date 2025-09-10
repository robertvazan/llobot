"""
Zoning system for mapping abstract zone names to filesystem paths.

This module provides a flexible way to define storage locations for different
types of data (e.g., caches, examples, knowledge archives) using abstract
"zones". A zone is a string identifier that gets resolved to a concrete
filesystem path.

This allows for easy configuration of data storage layouts. Two main types of
zoning are supported: prefix-based, where zones are subdirectories of a base
path, and wildcard-based, where a '*' in a path template is replaced by the
zone name.
"""
from __future__ import annotations
from functools import cache
from pathlib import Path
from typing import Callable

class Zoning:
    """Base class for zone resolvers."""
    def resolve(self, zone: str) -> Path:
        """
        Resolves a zone name to a filesystem path.

        Subclasses should override this method to implement their specific
        resolution logic.

        Args:
            zone: The abstract zone name.

        Returns:
            The concrete filesystem path for the zone.
        """
        raise NotImplementedError

    def __getitem__(self, zone: str) -> Path:
        """Convenience method to resolve a zone using dictionary-like access."""
        return self.resolve(zone)

def create_zoning(resolve: Callable[[str], Path]) -> Zoning:
    """
    Creates a Zoning instance from a resolve function.

    Args:
        resolve: A callable that takes a zone name and returns a `Path`.

    Returns:
        A `Zoning` instance that uses the provided function for resolution.
    """
    class LambdaZoning(Zoning):
        def resolve(self, zone: str) -> Path:
            return resolve(zone)
    return LambdaZoning()

@cache
def prefix_zoning(prefix: Path | str) -> Zoning:
    """
    Creates a zoning that resolves zones as subdirectories of a prefix.

    For example, `prefix_zoning('/data').resolve('cache')` returns `/data/cache`.

    Args:
        prefix: The base path for all zones.

    Returns:
        A `Zoning` instance for the given prefix.
    """
    prefix = Path(prefix).expanduser()
    return create_zoning(lambda zone: prefix / zone)

@cache
def wildcard_zoning(pattern: Path | str) -> Zoning:
    """
    Creates a zoning that replaces a wildcard in a path pattern with the zone name.

    For example, `wildcard_zoning('/data/*/files').resolve('images')`
    returns `/data/images/files`.

    Args:
        pattern: A path pattern containing a '*' wildcard.

    Returns:
        A `Zoning` instance for the given pattern.

    Raises:
        ValueError: If the pattern does not contain a wildcard.
    """
    pattern = Path(pattern).expanduser()
    if '*' not in str(pattern):
        raise ValueError
    return create_zoning(lambda zone: Path(*(part.replace('*', zone) for part in pattern.parts)))

def coerce_zoning(what: Zoning | Path | str) -> Zoning:
    """
    Coerces an object into a Zoning instance.

    - If `what` is already a `Zoning` instance, it is returned as is.
    - If `what` is a string or `Path` containing a wildcard ('*'),
      `wildcard_zoning` is used.
    - Otherwise, `prefix_zoning` is used.

    Args:
        what: The object to coerce.

    Returns:
        A `Zoning` instance.
    """
    if isinstance(what, Zoning):
        return what
    elif '*' in str(what):
        return wildcard_zoning(what)
    else:
        return prefix_zoning(what)

__all__ = [
    'Zoning',
    'create_zoning',
    'prefix_zoning',
    'wildcard_zoning',
    'coerce_zoning',
]
