"""
Project selection environment component.
"""
from __future__ import annotations
from functools import cached_property
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.projects.library.empty import EmptyProjectLibrary
from llobot.projects.union import union_project

class ProjectEnv:
    """
    An environment component that holds the currently selected projects.
    """
    _projects: set[Project]
    _library: ProjectLibrary

    def __init__(self):
        self._projects = set()
        self._library = EmptyProjectLibrary()

    def configure(self, library: ProjectLibrary):
        """
        Configures the project library to use for lookups.

        Args:
            library: The project library.
        """
        self._library = library

    def add(self, key: str) -> list[Project]:
        """
        Looks up projects by key and adds them to the environment.

        Projects are deduplicated by value. The cache for the `union` property
        is invalidated if any new projects are added.

        Args:
            key: The key to look up projects in the configured library.

        Returns:
            A list of matching projects that were found.
        """
        found = self._library.lookup(key)
        if found:
            initial_count = len(self._projects)
            for project in found:
                self._projects.add(project)
            if len(self._projects) > initial_count and 'union' in self.__dict__:
                del self.union
        return found

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
