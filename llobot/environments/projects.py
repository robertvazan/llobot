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
    _projects: set[Project]

    def __init__(self):
        self._projects = set()

    def add(self, project: Project):
        """
        Adds a project to the environment.

        Projects are deduplicated by object equality.

        Args:
            project: The project to add.
        """
        self._projects.add(project)
        if 'union' in self.__dict__:
            del self.union

    @property
    def selected(self) -> list[Project]:
        """
        Gets the list of all selected projects, sorted by zone for consistency.

        Returns:
            A sorted list of `Project` instances.
        """
        return sorted(list(self._projects), key=lambda p: sorted(list(p.zones)))

    @cached_property
    def union(self) -> Project:
        """
        Gets a union of all selected projects.

        Returns:
            A `Project` instance representing the union. This will be an `EmptyProject`
            if no projects are selected, or the project itself if only one is
            selected.
        """
        return union_project(*self.selected)

__all__ = [
    'ProjectEnv',
]
