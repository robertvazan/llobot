"""
Project selection environment component.
"""
from __future__ import annotations
from functools import cached_property
from pathlib import Path
from llobot.environments.persistent import PersistentEnv
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.projects.library.empty import EmptyProjectLibrary
from llobot.projects.union import union_project
from llobot.utils.fs import read_text, write_text

class ProjectEnv(PersistentEnv):
    """
    An environment component that holds the currently selected projects.
    It can be persisted by saving the keys of selected projects.
    """
    _projects: set[Project]
    _library: ProjectLibrary
    _keys: set[str]

    def __init__(self):
        self._projects = set()
        self._library = EmptyProjectLibrary()
        self._keys = set()

    def configure(self, library: ProjectLibrary):
        """
        Configures the project library to use for lookups.
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
            self._keys.add(key)
            initial_count = len(self._projects)
            self._projects.update(found)
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

    def save(self, directory: Path):
        """
        Saves the keys of selected projects to `projects.txt`.

        The file is created even if it's empty, containing one key per line, sorted.
        """
        content = '\n'.join(sorted(list(self._keys)))
        if content:
            content += '\n'
        write_text(directory / 'projects.txt', content)

    def load(self, directory: Path):
        """
        Loads project keys from `projects.txt`, clearing any prior state.

        This method assumes that a project library has already been configured via `configure()`.
        If the `projects.txt` file doesn't exist, the project selection is simply cleared.

        Args:
            directory: The directory to load the state from.

        Raises:
            ValueError: If a key from `projects.txt` does not match any project.
        """
        # Clear prior state
        self._projects.clear()
        self._keys.clear()
        if 'union' in self.__dict__:
            del self.union

        path = directory / 'projects.txt'
        if not path.exists():
            return

        content = read_text(path)
        keys = {line.strip() for line in content.splitlines() if line.strip()}

        for key in sorted(list(keys)):
            if not self.add(key):
                raise ValueError(f"Project key '{key}' from projects.txt not found in library.")

__all__ = [
    'ProjectEnv',
]
