from pathlib import Path
from llobot.projects.directory import DirectoryProject
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.parsing import parse_pattern

def test_directory_project_simple(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.py").write_text("content3")

    project = DirectoryProject(tmp_path)
    assert project.name == tmp_path.name

    expected_index = KnowledgeIndex([
        Path(f'{tmp_path.name}/file1.txt'),
        Path(f'{tmp_path.name}/file2.txt'),
        Path(f'{tmp_path.name}/subdir/file3.py'),
    ])
    assert project.enumerate() == expected_index

    expected_knowledge = Knowledge({
        Path(f'{tmp_path.name}/file1.txt'): 'content1\n',
        Path(f'{tmp_path.name}/file2.txt'): 'content2\n',
        Path(f'{tmp_path.name}/subdir/file3.py'): 'content3\n',
    })
    assert project.load() == expected_knowledge

def test_directory_project_no_prefix(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    project = DirectoryProject(tmp_path, prefix=Path('.'))
    assert project.enumerate() == KnowledgeIndex([Path('file1.txt')])
    assert project.load() == Knowledge({Path('file1.txt'): 'content1\n'})

def test_directory_project_custom_name(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    project = DirectoryProject(tmp_path, name="my-proj")
    assert project.name == "my-proj"
    assert project.enumerate() == KnowledgeIndex([Path('my-proj/file1.txt')])

def test_directory_project_filtering(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "blacklisted_dir").mkdir()
    (tmp_path / "blacklisted_dir" / "file3.txt").write_text("content3")
    (tmp_path / "blacklisted_file.txt").write_text("content4")


    project = DirectoryProject(
        tmp_path,
        prefix=Path('.'),
        whitelist=SuffixSubset(".txt"),
        blacklist=parse_pattern('*blacklisted*')
    )

    assert project.enumerate() == KnowledgeIndex([Path('file1.txt')])
