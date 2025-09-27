"""
Wildcard-based zoning.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import Zoning, validate_zone

class WildcardZoning(Zoning, ValueTypeMixin):
    """
    Replaces a wildcard in a path pattern with the zone name.

    For example, `WildcardZoning('/data/*/files').resolve(Path('images'))`
    returns `/data/images/files`.
    """
    _pattern: Path

    def __init__(self, pattern: Path | str):
        """
        Initializes the wildcard-based zoning.

        Args:
            pattern: A path pattern containing a '*' wildcard.

        Raises:
            ValueError: If the pattern does not contain a wildcard.
        """
        self._pattern = Path(pattern).expanduser()
        if '*' not in str(self._pattern):
            raise ValueError(f"Wildcard pattern must contain '*': {self._pattern}")

    def resolve(self, zone: Path) -> Path:
        """
        Resolves a zone by replacing the wildcard in the pattern.

        Args:
            zone: The zone identifier to resolve.

        Returns:
            The resolved path.
        """
        validate_zone(zone)
        zone_str = zone.as_posix()
        return Path(*(part.replace('*', zone_str) for part in self._pattern.parts))

__all__ = [
    'WildcardZoning',
]
