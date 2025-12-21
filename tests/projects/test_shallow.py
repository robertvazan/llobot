from pathlib import Path, PurePosixPath
import pytest
from llobot.projects.directory import DirectoryProject
from llobot.projects.shallow import ShallowProject
from llobot.projects.items import ProjectFile, ProjectDirectory
from llobot.knowledge import Knowledge

def test_shallow_project(tmp_path: Path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "file1.txt").write_text("1")
    (project_dir / "subdir").mkdir()
    (project_dir / "subdir" / "file2.txt").write_text("2")

    base_project = DirectoryProject(project_dir, prefix="p")
    shallow = ShallowProject(base_project)

    assert shallow.zones == base_project.zones
    assert shallow.prefixes == base_project.prefixes

    # items() should return shallow files and directories
    assert set(shallow.items(PurePosixPath("p"))) == {
        ProjectFile(PurePosixPath("p/file1.txt")),
        ProjectDirectory(PurePosixPath("p/subdir")),
    }
    assert shallow.items(PurePosixPath("p/subdir")) == []

    # read_all() should only read shallow files
    assert shallow.read_all() == Knowledge({PurePosixPath("p/file1.txt"): "1\n"})

    # read()
    assert shallow.read(PurePosixPath("p/file1.txt")) == "1\n"
    assert shallow.read(PurePosixPath("p/subdir/file2.txt")) is None

def test_shallow_project_mutable(tmp_path: Path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "file1.txt").write_text("1")
    (project_dir / "subdir").mkdir()
    (project_dir / "subdir" / "file2.txt").write_text("2")

    base_project = DirectoryProject(project_dir, prefix="p", mutable=True)
    shallow = ShallowProject(base_project)

    # mutable()
    assert shallow.mutable(PurePosixPath("p/file1.txt"))
    assert not shallow.mutable(PurePosixPath("p/subdir/file2.txt"))
    assert shallow.mutable(PurePosixPath("p/new_file.txt")) # for writing new file

    # write()
    shallow.write(PurePosixPath("p/new_file.txt"), "new")
    assert (project_dir / "new_file.txt").read_text() == "new"
    with pytest.raises(PermissionError, match="Path is not shallow"):
        shallow.write(PurePosixPath("p/subdir/new_file.txt"), "fail")

    # remove()
    shallow.remove(PurePosixPath("p/file1.txt"))
    assert not (project_dir / "file1.txt").exists()
    with pytest.raises(PermissionError, match="Path is not shallow"):
        shallow.remove(PurePosixPath("p/subdir/file2.txt"))

    # move() via base Project implementation
    (project_dir / "source.txt").write_text("move")
    shallow.move(PurePosixPath("p/source.txt"), PurePosixPath("p/dest.txt"))
    assert not (project_dir / "source.txt").exists()
    assert (project_dir / "dest.txt").read_text() == "move\n"

    (project_dir / "subdir" / "source_deep.txt").write_text("deep")
    with pytest.raises(FileNotFoundError): # read fails for source
         shallow.move(PurePosixPath("p/subdir/source_deep.txt"), PurePosixPath("p/dest.txt"))

    (project_dir / "source.txt").write_text("move again")
    with pytest.raises(PermissionError): # mutable fails for destination
         shallow.move(PurePosixPath("p/source.txt"), PurePosixPath("p/subdir/dest_deep.txt"))
