"""A project library that looks up projects by prefix."""
from __future__ import annotations
from llobot.projects import Project, ProjectPrecursor, coerce_project
from llobot.projects.library import ProjectLibrary
from llobot.utils.values import ValueTypeMixin

class PrefixKeyedProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that looks up projects from a predefined list by matching
    their prefixes against the lookup key.
    """
    _projects: tuple[Project, ...]

    def __init__(self, *projects: ProjectPrecursor):
        """
        Initializes a new `PrefixKeyedProjectLibrary`.

        Args:
            *projects: A list of projects to include in the library.

        Raises:
            ValueError: If a project has no prefixes, or if two projects
                        share the same prefix.
        """
        self._projects = tuple(coerce_project(p) for p in projects)

        seen_prefixes = set()
        for p in self._projects:
            if not p.prefixes:
                raise ValueError(f"Project in PrefixKeyedProjectLibrary must have at least one prefix: {p}")
            for prefix in p.prefixes:
                if prefix in seen_prefixes:
                    raise ValueError(f"Duplicate prefix '{prefix}' in PrefixKeyedProjectLibrary")
                seen_prefixes.add(prefix)

    def lookup(self, key: str) -> list[Project]:
        """
        Finds all projects that have a prefix matching the key.

        Args:
            key: The lookup key to match against project prefixes.

        Returns:
            A list of matching projects.
        """
        found = []
        for p in self._projects:
            if any(str(prefix) == key for prefix in p.prefixes):
                found.append(p)
        return found

__all__ = ['PrefixKeyedProjectLibrary']
