from unittest.mock import Mock
from llobot.projects.dummy import DummyProject
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.indexes import KnowledgeIndex

def test_dummy_project():
    project = DummyProject("dummy")
    assert project.name == "dummy"
    assert project.enumerate() == KnowledgeIndex()
    assert project.load() == Knowledge()

    archive = Mock(spec=KnowledgeArchive)
    project.refresh(archive)
    archive.refresh.assert_not_called()

    assert project.last(archive) == Knowledge()
    archive.last.assert_not_called()
