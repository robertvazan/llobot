from __future__ import annotations
from datetime import datetime
from pathlib import Path
import pytest
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset, match_filename, match_suffix
from llobot.projects import Project
from llobot.projects.directory import DirectoryProject
from llobot.projects.none import NoProject
from llobot.projects.union import UnionProject, union_project

class MockProject(Project):
    def __init__(self, name: str, files: dict[str, str | dict], prefix: Path | None = None):
        self._name = name
        self._files = files
        self._prefix = prefix if prefix is not None else Path(name)
        self._whitelist = super().whitelist
        self._blacklist = super().blacklist

    @property
    def name(self) -> str:
        return self._name

    @property
    def whitelist(self) -> KnowledgeSubset:
        return self._whitelist

    @whitelist.setter
    def whitelist(self, value: KnowledgeSubset):
        self._whitelist = value

    @property
    def blacklist(self) -> KnowledgeSubset:
        return self._blacklist

    @blacklist.setter
    def blacklist(self, value: KnowledgeSubset):
        self._blacklist = value

    def _get_at(self, path: Path):
        node = self._files
        try:
            for part in path.parts:
                if part != '.':
                    node = node[part]
        except (KeyError, TypeError):
            return None
        return node

    def _to_local_path(self, path: Path) -> Path | None:
        """Strips the project prefix from a path. Returns None if path is not under the prefix."""
        if self._prefix == Path('.') or path.is_relative_to(self._prefix):
            return path.relative_to(self._prefix) if self._prefix != Path('.') else path
        return None

    def list_files(self, path: Path) -> list[str]:
        local_path = self._to_local_path(path)
        if local_path is None:
            return []
        node = self._get_at(local_path)
        if isinstance(node, dict):
            return [name for name, content in node.items() if isinstance(content, str)]
        return []

    def list_subdirs(self, path: Path) -> list[str]:
        local_path = self._to_local_path(path)
        if local_path is not None:
            node = self._get_at(local_path)
            if isinstance(node, dict):
                return [name for name, content in node.items() if isinstance(content, dict)]
            return []

        if self._prefix != Path('.') and self._prefix.is_relative_to(path):
            relative_prefix = self._prefix.relative_to(path)
            return [relative_prefix.parts[0]] if relative_prefix.parts else []
        return []

    def read(self, path: Path) -> str | None:
        local_path = self._to_local_path(path)
        if local_path is None:
            return None
        content = self._get_at(local_path)
        return content if isinstance(content, str) else None

def test_no_project():
    project = NoProject()
    with pytest.raises(NotImplementedError):
        _ = project.name
    assert project.enumerate() == KnowledgeIndex()
    assert project.load() == Knowledge()

def test_union_project():
    p1 = MockProject("p1", {"a.txt": "a", "b.py": "b"})
    p2 = MockProject("p2", {"c.txt": "c", "d.py": "d"})

    union = union_project(p1, p2)
    assert (union | p1) is not None # test operator

    expected_index = KnowledgeIndex([Path("p1/a.txt"), Path("p1/b.py"), Path("p2/c.txt"), Path("p2/d.py")])
    assert union.enumerate() == expected_index

    expected_knowledge = Knowledge({
        Path("p1/a.txt"): "a",
        Path("p1/b.py"): "b",
        Path("p2/c.txt"): "c",
        Path("p2/d.py"): "d",
    })
    assert union.load() == expected_knowledge

    assert union.read(Path("p1/a.txt")) == "a"
    assert union.read(Path("p2/c.txt")) == "c"
    assert union.read(Path("nonexistent")) is None
    assert sorted(union.list_subdirs(Path("."))) == ['p1', 'p2']

def test_union_project_factory():
    p1 = MockProject("p1", {})
    assert union_project() == NoProject()
    assert union_project(p1) is p1
    assert isinstance(union_project(p1, p1), UnionProject)

def test_union_project_flattening():
    p1 = MockProject("p1", {})
    p2 = MockProject("p2", {})
    p3 = MockProject("p3", {})
    union1 = union_project(p1, p2)
    union2 = union_project(union1, p3)
    assert isinstance(union2, UnionProject)
    assert union2._projects == [p1, p2, p3]

def test_union_project_whitelist_blacklist():
    p1 = MockProject("p1", {"a.txt": "a", "b.py": "b", "c.txt": "c"})
    p1.whitelist = match_suffix(".txt")
    p1.blacklist = match_filename("c.txt")

    p2 = MockProject("p2", {"d.txt": "d", "e.py": "e"})
    p2.blacklist = match_filename("e.py")

    union = union_project(p1, p2)

    expected_index = KnowledgeIndex([
        Path("p1/a.txt"),
        Path("p2/d.txt"),
    ])
    assert union.enumerate() == expected_index
