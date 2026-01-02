from pathlib import Path
import pytest
from llobot.projects import coerce_project
from llobot.projects.directory import DirectoryProject
from llobot.projects.zone import ZoneProject

def test_coerce_project(tmp_path: Path):
    p_zone = ZoneProject('p_zone')
    assert coerce_project(p_zone) is p_zone

    p_dir = DirectoryProject(tmp_path)
    assert coerce_project(p_dir) is p_dir

    assert coerce_project(tmp_path) == p_dir
    assert coerce_project(str(tmp_path)) == p_dir
    assert coerce_project('~/dummy')._directory == (Path.home() / 'dummy').absolute()

    assert coerce_project('my-zone') == ZoneProject('my-zone')
    assert coerce_project('my/zone') == ZoneProject('my/zone')

    with pytest.raises(TypeError):
        coerce_project(123)
