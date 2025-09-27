from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.projects.empty import EmptyProject

def test_empty_project():
    project = EmptyProject()
    assert project.zones == set()
    assert project.prefixes == set()
    assert project.items(Path('.')) == []
    assert project.read_all() == Knowledge()
    assert project == EmptyProject()
