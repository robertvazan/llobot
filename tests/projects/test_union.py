from __future__ import annotations
from pathlib import Path
import pytest
from llobot.knowledge import Knowledge
from llobot.projects import Project
from llobot.projects.directory import DirectoryProject
from llobot.projects.empty import EmptyProject
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem
from llobot.projects.union import UnionProject, union_project
from llobot.utils.values import ValueTypeMixin

class MockProject(Project, ValueTypeMixin):
    def __init__(self, zones: set[str], prefixes: set[str], files: dict[str, str | dict]):
        self._zones = {Path(z) for z in zones}
        self._prefixes = {Path(p) for p in prefixes}
        self._files = files
        self._tracked = True

    @property
    def zones(self) -> set[Path]:
        return self._zones

    @property
    def prefixes(self) -> set[Path]:
        return self._prefixes

    def _get_at(self, path: Path):
        node = self._files
        try:
            for part in path.parts:
                if part != '.':
                    node = node[part]
        except (KeyError, TypeError):
            return None
        return node

    def items(self, path: Path) -> list[ProjectItem]:
        for prefix in self.prefixes:
            if path == prefix or path.is_relative_to(prefix):
                local_path = path.relative_to(prefix)
                node = self._get_at(local_path)
                if isinstance(node, dict):
                    result = []
                    for name, content in node.items():
                        item_path = path / name
                        if isinstance(content, str):
                            result.append(ProjectFile(item_path))
                        elif isinstance(content, dict):
                            result.append(ProjectDirectory(item_path))
                    return sorted(result, key=lambda i: i.path)
        return []

    def read(self, path: Path) -> str | None:
        for prefix in self.prefixes:
            if path == prefix or path.is_relative_to(prefix):
                local_path = path.relative_to(prefix)
                content = self._get_at(local_path)
                return content if isinstance(content, str) else None
        return None

    def tracked(self, item: ProjectItem) -> bool:
        return self._tracked

def test_union_project():
    p1 = MockProject(zones={'p1z'}, prefixes={'p1'}, files={"a.txt": "a", "b.py": "b"})
    p2 = MockProject(zones={'p2z'}, prefixes={'p2'}, files={"c.txt": "c", "d.py": "d"})

    union = union_project(p1, p2)
    assert (union | p1) is not None # test operator

    assert union.zones == {Path("p1z"), Path("p2z")}
    assert union.prefixes == {Path("p1"), Path("p2")}

    expected_knowledge = Knowledge({
        Path("p1/a.txt"): "a",
        Path("p1/b.py"): "b",
        Path("p2/c.txt"): "c",
        Path("p2/d.py"): "d",
    })
    assert union.read_all() == expected_knowledge

    assert union.read(Path("p1/a.txt")) == "a"
    assert union.read(Path("p2/c.txt")) == "c"
    assert union.read(Path("nonexistent")) is None

def test_union_project_factory():
    p1 = MockProject({"p1z"}, {"p1"}, {})
    assert union_project() == EmptyProject()
    assert union_project(p1) is p1
    assert isinstance(union_project(p1, p1), UnionProject)

def test_union_project_flattening():
    p1 = MockProject({"p1z"}, {"p1"}, {})
    p2 = MockProject({"p2z"}, {"p2"}, {})
    p3 = MockProject({"p3z"}, {"p3"}, {})
    union1 = union_project(p1, p2)
    union2 = union_project(union1, p3)
    assert isinstance(union2, UnionProject)
    assert union2._projects == (p1, p2, p3)

def test_union_duplicate_prefix_fails():
    p1 = MockProject(zones={'z1'}, prefixes={'p'}, files={})
    p2 = MockProject(zones={'z2'}, prefixes={'p'}, files={})
    with pytest.raises(ValueError, match="Duplicate prefix"):
        union_project(p1, p2)

def test_union_nested_prefix_allowed():
    p1 = MockProject(zones={'z1'}, prefixes={'p/a'}, files={'x': 'y'})
    p2 = MockProject(zones={'z2'}, prefixes={'p'}, files={'a': {}})
    union = union_project(p1, p2)
    assert union.read(Path('p/a/x')) == 'y'
    assert union.items(Path('p')) == [ProjectDirectory(Path('p/a'))]
    assert union.items(Path('p/a')) == [ProjectFile(Path('p/a/x'))]

def test_union_project_mutable(tmp_path: Path):
    dir1 = tmp_path / "p1"
    dir1.mkdir()
    (dir1 / "a.txt").write_text("a")
    dir2 = tmp_path / "p2"
    dir2.mkdir()
    (dir2 / "b.txt").write_text("b")

    p1 = DirectoryProject(dir1, prefix="p1", mutable=True)
    p2 = DirectoryProject(dir2, prefix="p2", mutable=False)
    union = union_project(p1, p2)

    assert union.mutable(Path("p1/a.txt"))
    assert not union.mutable(Path("p2/b.txt"))
    assert not union.mutable(Path("p3/c.txt"))

    union.write(Path("p1/c.txt"), "c")
    assert (dir1 / "c.txt").read_text() == "c"

    with pytest.raises(PermissionError):
        union.write(Path("p2/d.txt"), "d")

    union.remove(Path("p1/a.txt"))
    assert not (dir1 / "a.txt").exists()

    union.move(Path("p1/c.txt"), Path("p1/d.txt"))
    assert not (dir1 / "c.txt").exists()
    assert (dir1 / "d.txt").read_text() == "c\n"

def test_union_project_move_across_projects(tmp_path: Path):
    dir1 = tmp_path / "p1"
    dir1.mkdir()
    (dir1 / "a.txt").write_text("a")
    dir2 = tmp_path / "p2"
    dir2.mkdir()

    p1 = DirectoryProject(dir1, prefix="p1", mutable=True)
    p2 = DirectoryProject(dir2, prefix="p2", mutable=True)
    union = union_project(p1, p2)

    union.move(Path("p1/a.txt"), Path("p2/b.txt"))
    assert not (dir1 / "a.txt").exists()
    assert (dir2 / "b.txt").read_text() == "a\n"

    # Move from mutable to immutable should fail
    p2_immutable = DirectoryProject(dir2, prefix="p2", mutable=False)
    union_mixed = union_project(p1, p2_immutable)
    (dir1 / "x.txt").write_text("x")
    with pytest.raises(PermissionError, match="Destination path is not mutable"):
        union_mixed.move(Path("p1/x.txt"), Path("p2/y.txt"))
    assert (dir1 / "x.txt").exists()
    assert not (dir2 / "y.txt").exists()
