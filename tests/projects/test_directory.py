import os
import stat
from pathlib import Path, PurePosixPath
import pytest
from llobot.projects.directory import DirectoryProject
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.parsing import parse_pattern
from llobot.projects.items import ProjectDirectory, ProjectFile

def test_directory_project_simple(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.py").write_text("content3")

    project = DirectoryProject(tmp_path)
    # For paths not under home, prefix equals directory name
    prefix = PurePosixPath(tmp_path.name)
    if not tmp_path.is_relative_to(Path.home()):
        assert project.prefixes == {prefix}
    prefix = list(project.prefixes)[0]

    expected_paths = {
        prefix / 'file1.txt',
        prefix / 'file2.txt',
        prefix / 'subdir' / 'file3.py',
    }
    assert {file.path for file in project._walk(prefix)} == expected_paths

    expected_knowledge = Knowledge({
        prefix / 'file1.txt': 'content1\n',
        prefix / 'file2.txt': 'content2\n',
        prefix / 'subdir' / 'file3.py': 'content3\n',
    })
    assert project.read_all() == expected_knowledge

def test_directory_project_home_relative_prefix(tmp_path: Path, monkeypatch):
    """Test that directories under home get home-relative prefix by default."""
    # Create a fake home directory
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: fake_home))

    # Create a nested project under fake home
    project_dir = fake_home / "Sources" / "myproject"
    project_dir.mkdir(parents=True)
    (project_dir / "file.txt").write_text("content")

    project = DirectoryProject(project_dir)

    # Prefix should be home-relative path
    assert project.prefixes == {PurePosixPath("Sources/myproject")}
    # Files should be accessible via the home-relative prefix
    assert project.read(PurePosixPath("Sources/myproject/file.txt")) == "content\n"

def test_directory_project_outside_home_prefix(tmp_path: Path, monkeypatch):
    """Test that directories outside home use directory name as prefix."""
    # Create a fake home that doesn't contain tmp_path
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: fake_home))

    # Create a project outside fake home
    project_dir = tmp_path / "outside_project"
    project_dir.mkdir()
    (project_dir / "file.txt").write_text("content")

    project = DirectoryProject(project_dir)

    # Prefix should be just directory name (not home-relative)
    assert project.prefixes == {PurePosixPath("outside_project")}

def test_directory_project_at_home_uses_dirname(tmp_path: Path, monkeypatch):
    """Test that a project at home directory itself uses directory name as prefix."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    (fake_home / "file.txt").write_text("content")
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: fake_home))

    project = DirectoryProject(fake_home)

    # When directory is home itself, fall back to directory name
    assert project.prefixes == {PurePosixPath("fake_home")}
    assert project.read(PurePosixPath("fake_home/file.txt")) == "content\n"

def test_directory_project_dot_prefix_fails(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    with pytest.raises(ValueError, match="Zone must be a non-empty relative path other than '.'"):
        DirectoryProject(tmp_path, prefix=PurePosixPath('.'))

def test_directory_project_home_expansion():
    project = DirectoryProject('~/project', prefix='p')
    assert project._directory == (Path.home() / "project").absolute()

def test_directory_project_custom_zones(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    project = DirectoryProject(tmp_path, prefix="myprefix")
    assert project.prefixes == {PurePosixPath("myprefix")}
    assert {file.path for file in project._walk(PurePosixPath("myprefix"))} == {PurePosixPath("myprefix/file1.txt")}

def test_directory_project_filtering(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "blacklisted_dir").mkdir()
    (tmp_path / "blacklisted_dir" / "file3.txt").write_text("content3")
    (tmp_path / "blacklisted_file.txt").write_text("content4")


    project = DirectoryProject(
        tmp_path,
        prefix=PurePosixPath('p'),
        whitelist=SuffixSubset(".txt"),
        blacklist=parse_pattern('**/blacklisted*')
    )

    assert {file.path for file in project._walk(PurePosixPath('p'))} == {PurePosixPath('p/file1.txt')}
    assert project.read_all() == Knowledge({PurePosixPath('p/file1.txt'): 'content1\n'})

def test_items(tmp_path: Path):
    (tmp_path / "file.txt").write_text("content")
    (tmp_path / "subdir").mkdir()
    project = DirectoryProject(tmp_path)
    prefix = PurePosixPath(tmp_path.name)

    assert project.items(PurePosixPath(tmp_path.name, 'nonexistent')) == []

    prefix_items = project.items(prefix)
    assert set(prefix_items) == {
        ProjectFile(prefix / "file.txt"),
        ProjectDirectory(prefix / "subdir"),
    }

def test_directory_project_mutable(tmp_path: Path):
    project_dir = tmp_path / "mutable_project"
    project_dir.mkdir()
    (project_dir / "file.txt").write_text("initial")

    project = DirectoryProject(project_dir, prefix="p", mutable=True)
    assert project.mutable(PurePosixPath("p/file.txt"))
    assert not project.mutable(PurePosixPath("q/file.txt"))

    # Test write
    project.write(PurePosixPath("p/new_file.txt"), "new content")
    assert (project_dir / "new_file.txt").read_text() == "new content"

    # Test update (via write)
    project.write(PurePosixPath("p/file.txt"), "updated")
    assert (project_dir / "file.txt").read_text() == "updated"

    # Test remove
    assert (project_dir / "file.txt").exists()
    project.remove(PurePosixPath("p/file.txt"))
    assert not (project_dir / "file.txt").exists()

    # Test remove non-existent
    with pytest.raises(FileNotFoundError):
        project.remove(PurePosixPath("p/non_existent_file.txt"))

    # Test remove directory
    (project_dir / "subdir").mkdir()
    with pytest.raises(IsADirectoryError):
        project.remove(PurePosixPath("p/subdir"))

    # Test move
    (project_dir / "source.txt").write_text("move me")
    project.move(PurePosixPath("p/source.txt"), PurePosixPath("p/dest.txt"))
    assert not (project_dir / "source.txt").exists()
    assert (project_dir / "dest.txt").read_text() == "move me"

    # Test write preserves permissions
    executable_path = project_dir / "executable.sh"
    executable_path.write_text("#!/bin/bash\necho hello")
    executable_path.chmod(0o755)
    original_mode = executable_path.stat().st_mode
    assert os.access(executable_path, os.X_OK)

    project.write(PurePosixPath("p/executable.sh"), "#!/bin/bash\necho world")
    assert (project_dir / "executable.sh").read_text() == "#!/bin/bash\necho world"
    new_mode = executable_path.stat().st_mode
    assert stat.S_IMODE(new_mode) == stat.S_IMODE(original_mode)
    assert os.access(executable_path, os.X_OK)

    # Test move preserves permissions
    executable_move_src_path = project_dir / "executable_move_src.sh"
    executable_move_src_path.write_text("#!/bin/bash\necho move")
    executable_move_src_path.chmod(0o755)
    src_mode = executable_move_src_path.stat().st_mode
    assert os.access(executable_move_src_path, os.X_OK)

    project.move(PurePosixPath("p/executable_move_src.sh"), PurePosixPath("p/executable_move_dest.sh"))

    executable_move_dest_path = project_dir / "executable_move_dest.sh"
    assert not executable_move_src_path.exists()
    assert executable_move_dest_path.exists()
    dest_mode = executable_move_dest_path.stat().st_mode
    assert stat.S_IMODE(dest_mode) == stat.S_IMODE(src_mode)
    assert os.access(executable_move_dest_path, os.X_OK)

def test_directory_project_immutable_write_fails(tmp_path: Path):
    project_dir = tmp_path / "immutable_project"
    project_dir.mkdir()

    project = DirectoryProject(project_dir, prefix="p")
    assert not project.mutable(PurePosixPath("p/some_file.txt"))

    with pytest.raises(PermissionError):
        project.write(PurePosixPath("p/file.txt"), "content")

    with pytest.raises(PermissionError):
        project.remove(PurePosixPath("p/file.txt"))

def test_directory_project_write_preserves_executable(tmp_path: Path):
    """
    Overwriting an existing executable file must preserve the executable bit.
    """
    project_dir = tmp_path / "exec_project"
    project_dir.mkdir()
    exe_path = project_dir / "run.sh"
    exe_path.write_text("#!/bin/bash\necho hello")
    exe_path.chmod(0o755)
    original_mode = exe_path.stat().st_mode
    assert os.access(exe_path, os.X_OK)

    project = DirectoryProject(project_dir, prefix="p", mutable=True)
    project.write(PurePosixPath("p/run.sh"), "#!/bin/bash\necho world")

    assert (project_dir / "run.sh").read_text() == "#!/bin/bash\necho world"
    new_mode = exe_path.stat().st_mode
    assert stat.S_IMODE(new_mode) == stat.S_IMODE(original_mode)
    assert os.access(exe_path, os.X_OK)

def test_directory_project_summary(tmp_path: Path):
    project_dir = tmp_path / "summary_project"
    project_dir.mkdir()

    # Test read-only
    project = DirectoryProject(project_dir, prefix="p", mutable=False)
    assert "Directory `~/p`, read-only" in project.summary[0]

    # Test mutable
    project = DirectoryProject(project_dir, prefix="p", mutable=True)
    assert "Directory `~/p`, mutable" in project.summary[0]

    # Test mapped path (when real path differs from expected home-relative path)
    # Assuming project_dir is not at ~/p
    if project_dir != Path.home() / "p":
        assert f"real location `{project_dir}`" in project.summary[0]

    # Test home-relative assumption
    assert len(project.summary) == 1

def test_directory_project_executable(tmp_path: Path):
    project_dir = tmp_path / "exec_project"
    project_dir.mkdir()
    (project_dir / "subdir").mkdir()

    # Test executable=False
    project = DirectoryProject(project_dir, prefix="p", executable=False)
    assert not project.executable(PurePosixPath("p/subdir"))
    with pytest.raises(PermissionError):
        project.execute(PurePosixPath("p/subdir"), "echo hello")

    # Test executable=True
    project = DirectoryProject(project_dir, prefix="p", executable=True)
    assert project.executable(PurePosixPath("p"))
    assert project.executable(PurePosixPath("p/subdir"))
    assert not project.executable(PurePosixPath("q"))

    # Test execute
    output = project.execute(PurePosixPath("p"), "echo hello")
    assert output.strip() == "hello"

    # Test execute with cwd
    output = project.execute(PurePosixPath("p/subdir"), "pwd")
    assert str(project_dir / "subdir") in output

    # Test execute with non-existent cwd
    with pytest.raises(FileNotFoundError):
        project.execute(PurePosixPath("p/nonexistent"), "pwd")

    # Test execute failing script
    with pytest.raises(RuntimeError) as excinfo:
        project.execute(PurePosixPath("p"), "exit 1")
    assert "exit code 1" in str(excinfo.value)

    # Test summary
    assert "executable" in project.summary[0]
