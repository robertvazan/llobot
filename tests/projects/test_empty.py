from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.projects.empty import EmptyProject

def test_empty_project():
    project = EmptyProject()
    assert project.prefixes == set()
    assert project.items(PurePosixPath('.')) == []
    assert project.read_all() == Knowledge()
    assert project == EmptyProject()
