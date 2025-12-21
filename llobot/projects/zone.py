"""
A project that only has zones.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.projects import Project
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import validate_zone

class ZoneProject(Project, ValueTypeMixin):
    """
    A project that has one or more zones but no content (no prefixes or items).

    This is useful for creating named groups of examples in `ExampleMemory`
    without associating them with a full-fledged `DirectoryProject`.
    """
    _zones: frozenset[PurePosixPath]

    def __init__(self, *zones: str | PurePosixPath):
        """
        Initializes a new ZoneProject.

        Args:
            *zones: One or more zone identifiers for the project.

        Raises:
            ValueError: If no zones are provided or if a zone is invalid.
        """
        if not zones:
            raise ValueError("ZoneProject must have at least one zone.")
        self._zones = frozenset(PurePosixPath(z) for z in zones)
        for zone in self._zones:
            if zone.is_absolute():
                raise ValueError(f"Project zone must be relative: {zone}")
            validate_zone(zone)

    @property
    def zones(self) -> set[PurePosixPath]:
        return set(self._zones)

__all__ = [
    'ZoneProject',
]
