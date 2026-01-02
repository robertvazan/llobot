"""
A project that only has prefixes (markers).
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.projects import Project
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import validate_zone
from llobot.formats.paths import coerce_path

class MarkerProject(Project, ValueTypeMixin):
    """
    A project that has one or more prefixes but no content.

    This is useful for creating named groups of examples in `ExampleMemory`
    without associating them with a full-fledged `DirectoryProject`.
    """
    _prefixes: frozenset[PurePosixPath]

    def __init__(self, *prefixes: str | PurePosixPath):
        """
        Initializes a new MarkerProject.

        Args:
            *prefixes: One or more prefix identifiers for the project.

        Raises:
            ValueError: If no prefixes are provided or if a prefix is invalid.
        """
        if not prefixes:
            raise ValueError("MarkerProject must have at least one prefix.")
        self._prefixes = frozenset(coerce_path(p) for p in prefixes)
        for prefix in self._prefixes:
            validate_zone(prefix)

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return set(self._prefixes)

    @property
    def summary(self) -> list[str]:
        return [f"Marker `~/{p}`" for p in sorted(self._prefixes)]

__all__ = [
    'MarkerProject',
]
