"""A project library that looks up projects by zone."""
from __future__ import annotations
from llobot.projects import Project, ProjectPrecursor, coerce_project
from llobot.projects.library import ProjectLibrary
from llobot.utils.values import ValueTypeMixin

class ZoneKeyedProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that looks up projects from a predefined list by matching
    their zones against the lookup key.
    """
    _projects: tuple[Project, ...]

    def __init__(self, *projects: ProjectPrecursor):
        """
        Initializes a new `ZoneKeyedProjectLibrary`.

        Args:
            *projects: A list of projects to include in the library.
        """
        self._projects = tuple(coerce_project(p) for p in projects)

    def lookup(self, key: str) -> list[Project]:
        """
        Finds all projects that have a zone matching the key.

        Args:
            key: The lookup key to match against project zones.

        Returns:
            A list of matching projects.
        """
        found = []
        for p in self._projects:
            if any(str(zone) == key for zone in p.zones):
                found.append(p)
        return found

__all__ = ['ZoneKeyedProjectLibrary']
