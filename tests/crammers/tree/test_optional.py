from pathlib import PurePosixPath
from llobot.crammers.tree.optional import OptionalTreeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.indexes import IndexFormat
from llobot.knowledge import Knowledge
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary

class MockIndexFormat(IndexFormat):
    def render(self, knowledge: Knowledge) -> str:
        return "File tree"

class MockProject(Project):
    def __init__(self, knowledge: Knowledge):
        self._knowledge = knowledge
    def read_all(self) -> Knowledge:
        return self._knowledge

class MockProjectLibrary(ProjectLibrary):
    def __init__(self, project: Project):
        self._project = project
    def lookup(self, key: str) -> list[Project]:
        return [self._project]

def setup_env(knowledge: Knowledge, budget: int) -> Environment:
    env = Environment()
    env[ContextEnv].builder.budget = budget

    # Configure ProjectEnv with a mock library and add a project
    project = MockProject(knowledge)
    library = MockProjectLibrary(project)
    env[ProjectEnv].configure(library)
    env[ProjectEnv].add('mock')

    return env

def test_cram_fits():
    """Tests that the tree is added when it fits the budget."""
    crammer = OptionalTreeCrammer(index_format=MockIndexFormat())
    knowledge = Knowledge({PurePosixPath("file.txt"): "content"})
    env = setup_env(knowledge, 1000)

    crammer.cram(env)
    assert "File tree" in env[ContextEnv].builder.build()

def test_cram_does_not_fit():
    """Tests that the tree is not added when it exceeds the budget."""
    crammer = OptionalTreeCrammer(index_format=MockIndexFormat())
    knowledge = Knowledge({PurePosixPath("file.txt"): "content"})
    env = setup_env(knowledge, 10) # Too small

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()

def test_cram_empty_knowledge():
    """Tests that nothing is added for empty knowledge."""
    crammer = OptionalTreeCrammer()
    knowledge = Knowledge()
    env = setup_env(knowledge, 1000)

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()
