from pathlib import Path
from typing import Any, cast
import pytest
from llobot.projects import coerce_project
from llobot.projects.directory import DirectoryProject
from llobot.projects.marker import MarkerProject

def test_coerce_project(tmp_path: Path):
    p_marker = MarkerProject('p_marker')
    assert coerce_project(p_marker) is p_marker

    p_dir = DirectoryProject(tmp_path)
    assert coerce_project(p_dir) is p_dir

    assert coerce_project(tmp_path) == p_dir
    assert coerce_project(str(tmp_path)) == p_dir
    p_dummy = coerce_project('~/dummy')
    assert isinstance(p_dummy, DirectoryProject)
    assert p_dummy.directory == (Path.home() / 'dummy').absolute()

    assert coerce_project('my-prefix') == MarkerProject('my-prefix')
    assert coerce_project('my/prefix') == MarkerProject('my/prefix')

    with pytest.raises(TypeError):
        coerce_project(cast(Any, 123))
