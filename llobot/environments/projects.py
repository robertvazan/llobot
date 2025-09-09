"""
Project selection environment component.
"""
from __future__ import annotations
from functools import cached_property
from llobot.projects import Project
from llobot.projects.union import union_project

class ProjectEnv:
    """
    An environment component that holds the currently selected projects.
    """
    _projects: dict[str, Project]

    def __init__(self):
        self._projects = {}

    def add(self, project: Project):
        """
        Adds a project to the environment.

        If a project with the same name already exists, it is replaced.

        Args:
            project: The project to add.
        """
        self._projects[project.name] = project
        if 'union' in self.__dict__:
            del self.union

    @property
    def selected(self) -> list[Project]:
        """
        Gets the list of all selected projects, sorted by name for consistency.

        Returns:
            A sorted list of `Project` instances.
        """
        return sorted(self._projects.values(), key=lambda p: p.name)

    @cached_property
    def union(self) -> Project:
        """
        Gets a union of all selected projects.

        Returns:
            A `Project` instance representing the union. This will be `NoProject`
            if no projects are selected, or the project itself if only one is
            selected.
        """
        return union_project(*self.selected)

__all__ = [
    'ProjectEnv',
]
