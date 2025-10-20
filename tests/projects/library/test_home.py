from pathlib import Path

import pytest

from llobot.knowledge.indexes import KnowledgeIndex
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.knowledge.subsets.parsing import parse_pattern

def test_home_project_library(tmp_path: Path):
    (tmp_path / 'project1').mkdir()
    (tmp_path / 'project1' / 'file.txt').write_text('content')

    lib = HomeProjectLibrary(tmp_path)
    found = lib.lookup('project1')
    assert len(found) == 1
    project = found[0]
    assert isinstance(project, DirectoryProject)
    assert project._directory == (tmp_path / 'project1').absolute()
    assert project.prefixes == {Path('project1')}
    assert project.read(Path('project1/file.txt')) == 'content\n'

    assert lib.lookup('nonexistent') == []
    assert lib.lookup('/absolute/path') == []
    assert lib.lookup('invalid/../path') == []

def test_home_project_library_with_filters(tmp_path: Path):
    (tmp_path / 'project2').mkdir()
    (tmp_path / 'project2' / 'a.txt').write_text('a')
    (tmp_path / 'project2' / 'b.py').write_text('b')

    whitelist = parse_pattern('*.txt')
    lib = HomeProjectLibrary(tmp_path, whitelist=whitelist)
    project = lib.lookup('project2')[0]
    assert isinstance(project, DirectoryProject)
    assert project.read_all().keys() == KnowledgeIndex([Path('project2/a.txt')])

def test_home_project_library_default_home():
    lib = HomeProjectLibrary()
    assert lib._home == Path.home().absolute()

def test_home_project_library_mutable(tmp_path: Path):
    (tmp_path / 'project3').mkdir()

    # Test mutable=True
    mutable_lib = HomeProjectLibrary(tmp_path, mutable=True)
    mutable_project = mutable_lib.lookup('project3')[0]

    assert isinstance(mutable_project, DirectoryProject)
    assert mutable_project.mutable(Path('project3/new.txt'))

    mutable_project.write(Path('project3/new.txt'), 'new')
    assert (tmp_path / 'project3' / 'new.txt').read_text() == 'new'

    # Test default is not mutable
    immutable_lib = HomeProjectLibrary(tmp_path)
    immutable_project = immutable_lib.lookup('project3')[0]

    assert not immutable_project.mutable(Path('project3/another.txt'))
    with pytest.raises(PermissionError):
        immutable_project.write(Path('project3/another.txt'), 'fail')
    assert not (tmp_path / 'project3' / 'another.txt').exists()
