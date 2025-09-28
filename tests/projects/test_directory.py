import os
from pathlib import Path
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
    prefix = Path(tmp_path.name)
    assert project.zones == {prefix}
    assert project.prefixes == {prefix}

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

def test_directory_project_dot_prefix_fails(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    with pytest.raises(ValueError, match="Zone must be a non-empty relative path other than '.'"):
        DirectoryProject(tmp_path, prefix=Path('.'))

def test_directory_project_home_expansion():
    project = DirectoryProject('~/project', prefix='p')
    assert project._directory == (Path.home() / "project").absolute()

def test_directory_project_custom_zones(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    project = DirectoryProject(tmp_path, zones={"my-proj-zone"})
    prefix = Path(tmp_path.name)
    assert project.zones == {Path("my-proj-zone")}
    assert project.prefixes == {prefix}
    assert {file.path for file in project._walk(prefix)} == {prefix / 'file1.txt'}

def test_directory_project_filtering(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "blacklisted_dir").mkdir()
    (tmp_path / "blacklisted_dir" / "file3.txt").write_text("content3")
    (tmp_path / "blacklisted_file.txt").write_text("content4")


    project = DirectoryProject(
        tmp_path,
        prefix=Path('p'),
        whitelist=SuffixSubset(".txt"),
        blacklist=parse_pattern('**/blacklisted*')
    )

    assert {file.path for file in project._walk(Path('p'))} == {Path('p/file1.txt')}
    assert project.read_all() == Knowledge({Path('p/file1.txt'): 'content1\n'})

def test_items(tmp_path: Path):
    (tmp_path / "file.txt").write_text("content")
    (tmp_path / "subdir").mkdir()
    project = DirectoryProject(tmp_path)
    prefix = Path(tmp_path.name)

    assert project.items(Path(tmp_path.name, 'nonexistent')) == []

    prefix_items = project.items(prefix)
    assert set(prefix_items) == {
        ProjectFile(prefix / "file.txt"),
        ProjectDirectory(prefix / "subdir"),
    }
