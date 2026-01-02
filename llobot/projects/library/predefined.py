"""A project library that maps fixed keys to fixed projects."""
from __future__ import annotations

from typing import Mapping

from llobot.projects import Project, ProjectPrecursor, coerce_project
from llobot.projects.library import ProjectLibrary
from llobot.utils.values import ValueTypeMixin


class PredefinedProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that maps fixed keys to fixed projects.

    This library provides a static mapping of keys to projects. Keys are matched
    exactly as strings without any path normalization or resolution. Each key
    maps to at most one project.
    """
    _projects: dict[str, Project]

    def __init__(self, projects: Mapping[str, ProjectPrecursor]):
        """
        Initializes a new `PredefinedProjectLibrary`.

        The provided projects are coerced to `Project` instances using
        `coerce_project()`.

        Args:
            projects: A mapping from keys to projects or project precursors.
        """
        self._projects = {k: coerce_project(p) for k, p in projects.items()}

    def lookup(self, key: str) -> list[Project]:
        """
        Looks up projects that match the given key.

        Args:
            key: The lookup key. Keys are matched exactly.

        Returns:
            A list containing the matching project, or an empty list if not found.
        """
        project = self._projects.get(key)
        if project is not None:
            return [project]
        return []


__all__ = ['PredefinedProjectLibrary']
