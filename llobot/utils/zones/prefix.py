"""
Prefix-based zoning.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import Zoning

class PrefixZoning(Zoning, ValueTypeMixin):
    """
    Resolves zones as subdirectories of a prefix.

    For example, `PrefixZoning('/data').resolve('cache')` returns `/data/cache`.
    """
    _prefix: Path

    def __init__(self, prefix: Path | str):
        """
        Initializes the prefix-based zoning.

        Args:
            prefix: The base path for all zones.
        """
        self._prefix = Path(prefix).expanduser()

    def resolve(self, zone: str) -> Path:
        """
        Resolves a zone by appending it to the prefix.

        Args:
            zone: The zone name to resolve.

        Returns:
            The resolved path.
        """
        return self._prefix / zone

__all__ = [
    'PrefixZoning',
]
