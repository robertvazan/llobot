"""
A project that only has zones.
"""
from __future__ import annotations
from pathlib import Path
from llobot.projects import Project
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import validate_zone

class ZoneProject(Project, ValueTypeMixin):
    """
    A project that has one or more zones but no content (no prefixes or items).

    This is useful for creating named groups of examples in `ExampleMemory`
    without associating them with a full-fledged `DirectoryProject`.
    """
    _zones: frozenset[Path]

    def __init__(self, *zones: str | Path):
        """
        Initializes a new ZoneProject.

        Args:
            *zones: One or more zone identifiers for the project.

        Raises:
            ValueError: If no zones are provided or if a zone is invalid.
        """
        if not zones:
            raise ValueError("ZoneProject must have at least one zone.")
        self._zones = frozenset(Path(z) for z in zones)
        for zone in self._zones:
            validate_zone(zone)

    @property
    def zones(self) -> set[Path]:
        return set(self._zones)

__all__ = [
    'ZoneProject',
]
