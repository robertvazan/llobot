from pathlib import PurePosixPath
import pytest
from llobot.knowledge import Knowledge
from llobot.projects.zone import ZoneProject

def test_zone_project():
    project = ZoneProject("zone1", "zone2/sub")
    assert project.zones == {PurePosixPath("zone1"), PurePosixPath("zone2/sub")}
    assert project.prefixes == set()
    assert project.read_all() == Knowledge()
    assert project == ZoneProject("zone2/sub", "zone1")

def test_zone_project_no_zones_fails():
    with pytest.raises(ValueError, match="must have at least one zone"):
        ZoneProject()

def test_zone_project_invalid_zone_fails():
    with pytest.raises(ValueError, match="absolute"):
        ZoneProject("/absolute/path")
    with pytest.raises(ValueError, match=r"must not contain '\.\.'"):
        ZoneProject("..")
    with pytest.raises(ValueError, match="wildcards"):
        ZoneProject("zone*")
