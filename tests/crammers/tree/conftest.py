import pytest
from pathlib import PurePosixPath
from typing import Iterable
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from llobot.projects.items import ProjectFile, ProjectItem
from llobot.projects.library import ProjectLibrary

class MockProject(Project):
    def __init__(self, items: list[str | ProjectItem], prefixes: list[str] = ['.']):
        self._prefixes = {PurePosixPath(p) for p in prefixes}
        self._items = []
        for i in items:
            if isinstance(i, str):
                self._items.append(ProjectFile(PurePosixPath(i)))
            else:
                self._items.append(i)
        self._items.sort(key=lambda i: i.path)

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return self._prefixes

    def walk(self, directory: PurePosixPath | None = None) -> Iterable[ProjectItem]:
        # Simple mock that returns all items regardless of directory structure or tracking
        return self._items

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
