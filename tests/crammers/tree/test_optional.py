from pathlib import PurePosixPath
from typing import Iterable
from llobot.chats.intent import ChatIntent
from llobot.crammers.tree.optional import OptionalTreeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from llobot.projects.items import ProjectFile, ProjectItem, ProjectLink
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

def setup_env(items: list[str | ProjectItem], prefixes: list[str] = ['.']) -> Environment:
    env = Environment()

    # Configure ProjectEnv with a mock library and add a project
    project = MockProject(items, prefixes)
    library = MockProjectLibrary(project)
    env[ProjectEnv].configure(library)
    env[ProjectEnv].add('mock')

    return env

def test_cram_fits():
    """Tests that the tree is added when it fits the budget."""
    crammer = OptionalTreeCrammer(budget=1000)
    env = setup_env(["prefix/file.txt"], prefixes=['prefix'])

    crammer.cram(env)

    thread = env[ContextEnv].builder.build()
    assert thread
    message = thread.messages[0]
    assert message.intent == ChatIntent.SYSTEM
    assert "file.txt" in message.content
    assert "~/prefix:" in message.content
    assert "~/.:" not in message.content

def test_cram_structure():
    """Tests the structure of the rendered tree."""
    crammer = OptionalTreeCrammer(budget=1000)
    # Mock project that returns items in order
    env = setup_env(["a/b", "a/c", "d"])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content

    # Expected groups:
    # d
    #
    # ~/a:
    # b
    # c

    assert "~/.:" not in content
    assert "~/a:" in content
    assert "d" in content
    assert "b" in content
    assert "c" in content

def test_cram_links():
    """Tests rendering of symlinks."""
    crammer = OptionalTreeCrammer(budget=1000)
    link = ProjectLink(PurePosixPath("link"), PurePosixPath("target"))
    env = setup_env([link])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content
    assert "link -> target" in content

def test_cram_does_not_fit():
    """Tests that the tree is not added when it exceeds the budget."""
    crammer = OptionalTreeCrammer(budget=10)
    env = setup_env(["long_filename_that_exceeds_budget.txt"])

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()

def test_cram_empty():
    """Tests that nothing is added for empty project."""
    crammer = OptionalTreeCrammer(budget=1000)
    env = setup_env([])

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()
