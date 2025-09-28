"""A project library that is a union of multiple libraries."""
from __future__ import annotations
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.utils.values import ValueTypeMixin

class UnionProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that merges results from multiple underlying libraries.
    """
    _libraries: tuple[ProjectLibrary, ...]

    def __init__(self, *libraries: ProjectLibrary):
        """
        Initializes a new `UnionProjectLibrary`.

        Args:
            *libraries: The libraries to combine.
        """
        flattened = []
        for library in libraries:
            if isinstance(library, UnionProjectLibrary):
                flattened.extend(library._libraries)
            else:
                flattened.append(library)
        self._libraries = tuple(flattened)

    def lookup(self, key: str) -> list[Project]:
        """
        Looks up projects in all member libraries and returns a merged,
        deduplicated list of results.

        Args:
            key: The lookup key.

        Returns:
            A list of unique matching projects.
        """
        # Using a dict to deduplicate projects by value.
        # Projects are value types, so this works.
        found = {p: None for lib in self._libraries for p in lib.lookup(key)}
        return list(found.keys())

__all__ = ['UnionProjectLibrary']
