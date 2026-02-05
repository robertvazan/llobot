import pytest
from pathlib import PurePosixPath
from typing import Iterable
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem
from llobot.projects.library import ProjectLibrary

class MockProject(Project):
    def __init__(self, items: list[str | ProjectItem], prefixes: list[str] = ['.']):
        self._prefixes = {PurePosixPath(p) for p in prefixes}
        self._items = []

        known_paths = set()

        def add(item: ProjectItem):
            if item.path in known_paths:
                return
            known_paths.add(item.path)
            self._items.append(item)

            # Synthesize parent directories
            parent = item.path.parent
            if parent == item.path: # Reached root '.' or some other root
                return

            # If item is at root '.', parent is '.'
            # But if item is 'a/b', parent is 'a'.
            # If item is 'a', parent is '.'.

            # We want to add 'a' if 'a/b' exists.
            # We want to add '.' only if we consider it a directory item?
            # Project items usually don't include '.' itself as an item unless we want to list it?
            # But we are adding parent directories.

            if parent == PurePosixPath('.'):
                return

            if parent not in known_paths:
                add(ProjectDirectory(parent))

        for i in items:
            if isinstance(i, str):
                add(ProjectFile(PurePosixPath(i)))
            else:
                add(i)

        self._items.sort(key=lambda i: i.path)

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return self._prefixes

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
        # Return items that are directly under path
        results = []
        for item in self._items:
            if item.path.parent == path:
                results.append(item)
        return results

    def tracked(self, item: ProjectItem) -> bool:
        return True

    def walk(self, directory: PurePosixPath | None = None) -> Iterable[ProjectItem]:
        if directory is None:
            # Return all items
            return self._items
        # Return items under directory (recursive)
        results = []
        for item in self._items:
            if item.path == directory or item.path.is_relative_to(directory):
                results.append(item)
        return results

class MockProjectLibrary(ProjectLibrary):
    def __init__(self, project: Project):
        self._project = project
    def lookup(self, key: str) -> list[Project]:
        return [self._project]

@pytest.fixture
def setup_env_fixture():
    def _setup_env(items: list[str | ProjectItem], prefixes: list[str] = ['.']) -> Environment:
        env = Environment()
        project = MockProject(items, prefixes)
        library = MockProjectLibrary(project)
        env[ProjectEnv].configure(library)
        env[ProjectEnv].add('mock')
        return env
    return _setup_env
