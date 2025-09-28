from pathlib import Path
import pytest
from llobot.projects import coerce_project
from llobot.projects.directory import DirectoryProject
from llobot.projects.zone import ZoneProject
from llobot.projects.library import coerce_project_library
from llobot.projects.library.zone import ZoneKeyedProjectLibrary

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

def test_coerce_project_library():
    p1 = ZoneProject('p1')
    p2 = ZoneProject('p2')

    lib = ZoneKeyedProjectLibrary(p1, p2)
    assert coerce_project_library(lib) is lib

    lib_from_single = coerce_project_library(p1)
    assert isinstance(lib_from_single, ZoneKeyedProjectLibrary)
    assert lib_from_single._projects == (p1,)

    lib_from_list = coerce_project_library([p1, p2])
    assert isinstance(lib_from_list, ZoneKeyedProjectLibrary)
    assert lib_from_list._projects == (p1, p2)

    with pytest.raises(TypeError):
        coerce_project_library(123)

    with pytest.raises(TypeError):
        coerce_project_library("just a string which is iterable")
