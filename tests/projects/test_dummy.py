from llobot.projects.dummy import DummyProject
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

def test_dummy_project():
    project = DummyProject("dummy")
    assert project.name == "dummy"
    assert project.enumerate() == KnowledgeIndex()
    assert project.load() == Knowledge()
