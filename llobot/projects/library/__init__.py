"""
Project libraries for looking up projects by key.

This package provides the `ProjectLibrary` interface and several implementations
for discovering and retrieving `Project` instances based on a string key.
Libraries can be combined using `|`, `&`, and `-` operators.

Submodules
----------
empty
    A library that contains no projects.
filtered
    A library that filters results from another library.
home
    A library that finds projects in a home directory.
predefined
    A library that maps fixed keys to fixed projects.
union
    A library that combines multiple libraries.
"""
from __future__ import annotations
from llobot.projects import Project
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

__all__ = [
    'ProjectLibrary',
]
