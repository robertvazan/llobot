from pathlib import Path
from llobot.projects.directory import DirectoryProject
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.filename import FilenameSubset
from llobot.knowledge.subsets.suffix import SuffixSubset

def test_project_read_all(tmp_path: Path):
    (tmp_path / "subdir" / "nested").mkdir(parents=True)
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "subdir" / "file3.txt").write_text("content3")
    (tmp_path / "subdir" / "nested" / "file4.py").write_text("content4")
    (tmp_path / "blacklisted.txt").write_text("blacklisted")

    project = DirectoryProject(
        tmp_path,
        blacklist=FilenameSubset("blacklisted.txt"),
        whitelist=SuffixSubset(".txt"),
    )
    prefix = Path(tmp_path.name)

    expected_knowledge = Knowledge({
        prefix / "file1.txt": "content1\n",
        prefix / "subdir/file3.txt": "content3\n",
    })
    # read_document normalizes newlines
    loaded = project.read_all()
    assert loaded == expected_knowledge
