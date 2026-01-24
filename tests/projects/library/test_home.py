from pathlib import Path, PurePosixPath

import pytest

from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.parsing import parse_pattern
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.projects.shallow import ShallowProject


def test_home_project_library(tmp_path: Path):
    (tmp_path / 'project1').mkdir()
    (tmp_path / 'project1' / 'file.txt').write_text('content')

    lib = HomeProjectLibrary(tmp_path, parents=False)
    found = lib.lookup('project1')
    assert len(found) == 1
    project = found[0]
    assert isinstance(project, DirectoryProject)
    assert project._directory == (tmp_path / 'project1').absolute()
    assert project.prefixes == {PurePosixPath('project1')}
    assert project.read(PurePosixPath('project1/file.txt')) == 'content\n'

    assert lib.lookup('nonexistent') == []
    assert lib.lookup('/absolute/path') == []
    assert lib.lookup('invalid/../path') == []


def test_home_project_library_home_relative_prefix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that prefixes become home-relative when project directories are under Path.home()."""
    fake_home = tmp_path / 'fake_home'
    fake_home.mkdir()
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: fake_home))

    sources = fake_home / 'Sources'
    sources.mkdir()

    (sources / 'myproject').mkdir()
    (sources / 'myproject' / 'file.txt').write_text('content')

    lib = HomeProjectLibrary(sources, parents=False)
    project = lib.lookup('myproject')[0]

    # Prefix follows DirectoryProject-style home-relative computation.
    assert project.prefixes == {PurePosixPath('Sources/myproject')}
    assert project.read(PurePosixPath('Sources/myproject/file.txt')) == 'content\n'


def test_home_project_library_with_parents(tmp_path: Path):
    (tmp_path / 'p' / 'sub').mkdir(parents=True)
    (tmp_path / 'p' / 'file1.txt').write_text('1')
    (tmp_path / 'p' / 'sub' / 'file2.txt').write_text('2')

    lib = HomeProjectLibrary(tmp_path, parents=True)

    # Test with one parent
    found = lib.lookup('p/sub')
    assert len(found) == 2

    main_project = found[0]
    assert isinstance(main_project, DirectoryProject)
    assert main_project.prefixes == {PurePosixPath('p/sub')}
    assert main_project.read_all() == Knowledge({PurePosixPath('p/sub/file2.txt'): '2\n'})

    parent_project = found[1]
    assert isinstance(parent_project, ShallowProject)
    assert parent_project.prefixes == {PurePosixPath('p')}
    assert parent_project.read_all() == Knowledge({PurePosixPath('p/file1.txt'): '1\n'})

    # Test with no parents (stops at home)
    found_no_parents = lib.lookup('p')
    assert len(found_no_parents) == 1
    assert isinstance(found_no_parents[0], DirectoryProject)
    assert found_no_parents[0].prefixes == {PurePosixPath('p')}


def test_home_project_library_with_filters(tmp_path: Path):
    (tmp_path / 'project2').mkdir()
    (tmp_path / 'project2' / 'a.txt').write_text('a')
    (tmp_path / 'project2' / 'b.py').write_text('b')

    whitelist = parse_pattern('*.txt')
    lib = HomeProjectLibrary(tmp_path, whitelist=whitelist, parents=False)
    project = lib.lookup('project2')[0]
    assert isinstance(project, DirectoryProject)
    assert project.read_all().keys() == KnowledgeIndex([PurePosixPath('project2/a.txt')])


def test_home_project_library_default_home():
    lib = HomeProjectLibrary()
    assert lib._home == Path.home().absolute()


def test_home_project_library_mutable(tmp_path: Path):
    (tmp_path / 'project3').mkdir()

    # Test mutable=True
    mutable_lib = HomeProjectLibrary(tmp_path, mutable=True, parents=False)
    mutable_project = mutable_lib.lookup('project3')[0]

    assert isinstance(mutable_project, DirectoryProject)
    assert mutable_project.mutable(PurePosixPath('project3/new.txt'))

    mutable_project.write(PurePosixPath('project3/new.txt'), 'new')
    assert (tmp_path / 'project3' / 'new.txt').read_text() == 'new'

    # Test default is not mutable
    immutable_lib = HomeProjectLibrary(tmp_path, parents=False)
    immutable_project = immutable_lib.lookup('project3')[0]

    assert not immutable_project.mutable(PurePosixPath('project3/another.txt'))
    with pytest.raises(PermissionError):
        immutable_project.write(PurePosixPath('project3/another.txt'), 'fail')
    assert not (tmp_path / 'project3' / 'another.txt').exists()


def test_home_project_library_executable(tmp_path: Path):
    (tmp_path / 'project4').mkdir()

    # Test executable=True
    exec_lib = HomeProjectLibrary(tmp_path, executable=True, parents=False)
    exec_project = exec_lib.lookup('project4')[0]

    assert isinstance(exec_project, DirectoryProject)
    assert exec_project.executable(PurePosixPath('project4'))

    output = exec_project.execute(PurePosixPath('project4'), 'echo hello').strip()
    assert '+ echo hello' in output
    assert '\nhello\n' in output
    assert 'Exit code: 0' in output

    # Test default is not executable
    noexec_lib = HomeProjectLibrary(tmp_path, parents=False)
    noexec_project = noexec_lib.lookup('project4')[0]

    assert not noexec_project.executable(PurePosixPath('project4'))
    with pytest.raises(PermissionError):
        noexec_project.execute(PurePosixPath('project4'), 'echo hello')
