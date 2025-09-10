"""
Zoning system for mapping abstract zone names to filesystem paths.

This package provides a flexible way to define storage locations for different
types of data (e.g., caches, examples, knowledge archives) using abstract
"zones". A zone is a string identifier that gets resolved to a concrete
filesystem path.

This allows for easy configuration of data storage layouts. Two main types of
zoning are supported: prefix-based, where zones are subdirectories of a base
path, and wildcard-based, where a '*' in a path template is replaced by the
zone name.

Submodules
----------
prefix
    Prefix-based zoning.
wildcard
    Wildcard-based zoning.
"""
from __future__ import annotations
from pathlib import Path

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

def coerce_zoning(what: Zoning | Path | str) -> Zoning:
    """
    Coerces an object into a Zoning instance.

    - If `what` is already a `Zoning` instance, it is returned as is.
    - If `what` is a string or `Path` containing a wildcard ('*'),
      `WildcardZoning` is used.
    - Otherwise, `PrefixZoning` is used.

    Args:
        what: The object to coerce.

    Returns:
        A `Zoning` instance.
    """
    if isinstance(what, Zoning):
        return what
    # Use local imports to avoid reexporting symbols.
    from llobot.utils.zones.prefix import PrefixZoning
    from llobot.utils.zones.wildcard import WildcardZoning
    if '*' in str(what):
        return WildcardZoning(what)
    else:
        return PrefixZoning(what)

__all__ = [
    'Zoning',
    'coerce_zoning',
]
