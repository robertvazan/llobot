"""A project library that is a union of multiple libraries."""
from __future__ import annotations
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.utils.values import ValueTypeMixin

class UnionProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that combines multiple libraries with precedence.

    Libraries are checked from right to left. The first library that returns a
    match for a given key shadows any subsequent libraries (those to its left).
    """
    _members: tuple[ProjectLibrary, ...]

    def __init__(self, *libraries: ProjectLibrary):
        """
        Initializes a new `UnionProjectLibrary`.

        Args:
            *libraries: The libraries to combine.
        """
        flattened = []
        for library in libraries:
            if isinstance(library, UnionProjectLibrary):
                flattened.extend(library._members)
            else:
                flattened.append(library)
        self._members = tuple(flattened)

    @property
    def members(self) -> tuple[ProjectLibrary, ...]:
        """The combined member libraries."""
        return self._members

    def lookup(self, key: str) -> list[Project]:
        """
        Looks up projects in member libraries.

        Members are checked from right to left (last added has highest priority).
        The first member that returns a non-empty list determines the result.

        Args:
            key: The lookup key.

        Returns:
            A list of matching projects from the winning library.
        """
        for library in reversed(self._members):
            found = library.lookup(key)
            if found:
                return found
        return []

__all__ = ['UnionProjectLibrary']
