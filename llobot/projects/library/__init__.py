"""
Project libraries for looking up projects by key.

This package provides the `ProjectLibrary` interface and several implementations
for discovering and retrieving `Project` instances based on a string key.
Libraries can be combined using `|`, `&`, and `-` operators.
"""
from __future__ import annotations
from typing import Iterable
from llobot.projects import Project, ProjectPrecursor, coerce_project
from llobot.knowledge.subsets import KnowledgeSubset

class ProjectLibrary:
    """
    Base class for project libraries, which find projects based on a key.
    """
    def lookup(self, key: str) -> list[Project]:
        """
        Looks up projects that match the given key.

        Args:
            key: The lookup key, typically a project name or path.

        Returns:
            A list of matching `Project` instances. The order is not significant.
        """
        return []

    def __or__(self, other: ProjectLibrary) -> ProjectLibrary:
        from llobot.projects.library.union import UnionProjectLibrary
        return UnionProjectLibrary(self, other)

    def __and__(self, other: KnowledgeSubset) -> ProjectLibrary:
        from llobot.projects.library.filtered import FilteredProjectLibrary
        return FilteredProjectLibrary(self, whitelist=other)

    def __sub__(self, other: KnowledgeSubset) -> ProjectLibrary:
        from llobot.projects.library.filtered import FilteredProjectLibrary
        return FilteredProjectLibrary(self, whitelist=~other)

type ProjectLibraryPrecursor = ProjectLibrary | Project | Iterable[ProjectPrecursor]

def coerce_project_library(precursor: ProjectLibraryPrecursor) -> ProjectLibrary:
    """
    Coerces a precursor object into a `ProjectLibrary`.

    - `ProjectLibrary` is returned as is.
    - A single `Project` is wrapped in a `ZoneKeyedProjectLibrary`.
    - An iterable of `ProjectPrecursor` items is converted to a `ZoneKeyedProjectLibrary`.

    Args:
        precursor: The object to coerce.

    Returns:
        A `ProjectLibrary` instance.
    """
    if isinstance(precursor, ProjectLibrary):
        return precursor
    if isinstance(precursor, Project):
        from llobot.projects.library.zone import ZoneKeyedProjectLibrary
        return ZoneKeyedProjectLibrary(precursor)
    # The check for Iterable must be after other types, because string is an iterable.
    if isinstance(precursor, Iterable) and not isinstance(precursor, str):
        from llobot.projects.library.zone import ZoneKeyedProjectLibrary
        return ZoneKeyedProjectLibrary(*precursor)
    raise TypeError(f"Cannot coerce {precursor} to ProjectLibrary")

__all__ = [
    'ProjectLibrary',
    'ProjectLibraryPrecursor',
    'coerce_project_library',
]
