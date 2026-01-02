from pathlib import PurePosixPath
import pytest
from llobot.knowledge import Knowledge
from llobot.projects.marker import MarkerProject

def test_marker_project():
    project = MarkerProject("prefix1", "prefix2/sub")
    assert project.prefixes == {PurePosixPath("prefix1"), PurePosixPath("prefix2/sub")}
    assert project.read_all() == Knowledge()
    assert project == MarkerProject("prefix2/sub", "prefix1")

def test_marker_project_no_prefixes_fails():
    with pytest.raises(ValueError, match="must have at least one prefix"):
        MarkerProject()

def test_marker_project_invalid_prefix_fails():
    with pytest.raises(ValueError, match="absolute"):
        MarkerProject("/absolute/path")
    with pytest.raises(ValueError, match=r"must not contain '\.\.'"):
        MarkerProject("..")
    with pytest.raises(ValueError, match="wildcards"):
        MarkerProject("prefix*")

def test_marker_project_summary():
    project = MarkerProject("p1", "p2")
    summary = project.summary
    assert len(summary) == 2
    assert "Marker `~/p1`" in summary
    assert "Marker `~/p2`" in summary
