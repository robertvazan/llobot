from __future__ import annotations
import os
import stat
from pathlib import Path, PurePosixPath
import pytest
from llobot.knowledge import Knowledge
from llobot.projects import Project
from llobot.projects.directory import DirectoryProject
from llobot.projects.empty import EmptyProject
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem
from llobot.projects.union import UnionProject, union_project
from llobot.utils.values import ValueTypeMixin

class MockProject(Project, ValueTypeMixin):
    def __init__(self, prefixes: set[str], files: dict[str, str | dict]):
        self._prefixes = frozenset(PurePosixPath(p) for p in prefixes)
        self._files = files
        self._tracked = True

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return set(self._prefixes)

    @property
    def summary(self) -> list[str]:
        return [f"MockProject {p}" for p in sorted(self.prefixes)]

    def _get_at(self, path: PurePosixPath):
        node = self._files
        try:
            for part in path.parts:
                if part != '.':
                    node = node[part]
        except (KeyError, TypeError):
            return None
        return node

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
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

    def read(self, path: PurePosixPath) -> str | None:
        for prefix in self.prefixes:
            if path == prefix or path.is_relative_to(prefix):
                local_path = path.relative_to(prefix)
                content = self._get_at(local_path)
                return content if isinstance(content, str) else None
        return None

    def tracked(self, item: ProjectItem) -> bool:
        return self._tracked

def test_union_project():
    p1 = MockProject(prefixes={'p1'}, files={"a.txt": "a", "b.py": "b"})
    p2 = MockProject(prefixes={'p2'}, files={"c.txt": "c", "d.py": "d"})

    union = union_project(p1, p2)
    assert (union | p1) is not None # test operator

    assert union.prefixes == {PurePosixPath("p1"), PurePosixPath("p2")}

    expected_knowledge = Knowledge({
        PurePosixPath("p1/a.txt"): "a",
        PurePosixPath("p1/b.py"): "b",
        PurePosixPath("p2/c.txt"): "c",
        PurePosixPath("p2/d.py"): "d",
    })
    assert union.read_all() == expected_knowledge

    assert union.read(PurePosixPath("p1/a.txt")) == "a"
    assert union.read(PurePosixPath("p2/c.txt")) == "c"
    assert union.read(PurePosixPath("nonexistent")) is None

def test_union_project_factory():
    p1 = MockProject({"p1"}, {})
    assert union_project() == EmptyProject()
    assert union_project(p1) is p1
    assert isinstance(union_project(p1, p1), UnionProject)

def test_union_project_flattening():
    p1 = MockProject({"p1"}, {})
    p2 = MockProject({"p2"}, {})
    p3 = MockProject({"p3"}, {})
    union1 = union_project(p1, p2)
    union2 = union_project(union1, p3)
    assert isinstance(union2, UnionProject)
    assert union2._projects == (p1, p2, p3)

def test_union_duplicate_prefix_fails():
    p1 = MockProject(prefixes={'p'}, files={'f1': 'content'})
    p2 = MockProject(prefixes={'p'}, files={'f2': 'content'})
    with pytest.raises(ValueError, match="Duplicate prefix"):
        union_project(p1, p2)

def test_union_nested_prefix_allowed():
    p1 = MockProject(prefixes={'p/a'}, files={'x': 'y'})
    p2 = MockProject(prefixes={'p'}, files={'a': {}})
    union = union_project(p1, p2)
    assert union.read(PurePosixPath('p/a/x')) == 'y'
    assert union.items(PurePosixPath('p')) == [ProjectDirectory(PurePosixPath('p/a'))]
    assert union.items(PurePosixPath('p/a')) == [ProjectFile(PurePosixPath('p/a/x'))]

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

    assert union.mutable(PurePosixPath("p1/a.txt"))
    assert not union.mutable(PurePosixPath("p2/b.txt"))
    assert not union.mutable(PurePosixPath("p3/c.txt"))

    union.write(PurePosixPath("p1/c.txt"), "c")
    assert (dir1 / "c.txt").read_text() == "c"

    with pytest.raises(PermissionError):
        union.write(PurePosixPath("p2/d.txt"), "d")

    union.remove(PurePosixPath("p1/a.txt"))
    assert not (dir1 / "a.txt").exists()

    union.move(PurePosixPath("p1/c.txt"), PurePosixPath("p1/d.txt"))
    assert not (dir1 / "c.txt").exists()
    assert (dir1 / "d.txt").read_text() == "c"

def test_union_project_move_across_projects(tmp_path: Path):
    dir1 = tmp_path / "p1"
    dir1.mkdir()
    (dir1 / "a.txt").write_text("a")
    dir2 = tmp_path / "p2"
    dir2.mkdir()

    p1 = DirectoryProject(dir1, prefix="p1", mutable=True)
    p2 = DirectoryProject(dir2, prefix="p2", mutable=True)
    union = union_project(p1, p2)

    union.move(PurePosixPath("p1/a.txt"), PurePosixPath("p2/b.txt"))
    assert not (dir1 / "a.txt").exists()
    assert (dir2 / "b.txt").read_text() == "a\n"

    # Move from mutable to immutable should fail
    p2_immutable = DirectoryProject(dir2, prefix="p2", mutable=False)
    union_mixed = union_project(p1, p2_immutable)
    (dir1 / "x.txt").write_text("x")
    with pytest.raises(PermissionError, match="Destination path is not mutable"):
        union_mixed.move(PurePosixPath("p1/x.txt"), PurePosixPath("p2/y.txt"))
    assert (dir1 / "x.txt").exists()
    assert not (dir2 / "y.txt").exists()

def test_union_project_move_within_project_preserves_permissions(tmp_path: Path):
    dir1 = tmp_path / "p1"
    dir1.mkdir()
    executable_path = dir1 / "executable.sh"
    executable_path.write_text("#!/bin/bash\necho hello")
    executable_path.chmod(0o755)

    p1 = DirectoryProject(dir1, prefix="p1", mutable=True)
    union = union_project(p1)

    src_mode = executable_path.stat().st_mode
    assert os.access(executable_path, os.X_OK)

    union.move(PurePosixPath("p1/executable.sh"), PurePosixPath("p1/moved.sh"))

    dest_path = dir1 / "moved.sh"
    assert not executable_path.exists()
    assert dest_path.exists()
    dest_mode = dest_path.stat().st_mode
    assert stat.S_IMODE(dest_mode) == stat.S_IMODE(src_mode)
    assert os.access(dest_path, os.X_OK)

def test_union_project_summary():
    p1 = MockProject(prefixes={'p1'}, files={})
    p2 = MockProject(prefixes={'p2'}, files={})
    union = union_project(p1, p2)

    summary = union.summary
    assert len(summary) == 2
    assert "MockProject p1" in summary
    assert "MockProject p2" in summary

def test_union_project_execution(tmp_path: Path):
    dir1 = tmp_path / "p1"
    dir1.mkdir()
    dir2 = tmp_path / "p2"
    dir2.mkdir()

    p1 = DirectoryProject(dir1, prefix="p1", executable=True)
    p2 = DirectoryProject(dir2, prefix="p2", executable=False)
    union = union_project(p1, p2)

    assert union.executable(PurePosixPath("p1"))
    assert not union.executable(PurePosixPath("p2"))

    # Execute in p1
    output = union.execute(PurePosixPath("p1"), "echo hi")
    assert "\nhi\n" in output
    assert "Exit code: 0" in output

    # Execute in p2 should fail
    with pytest.raises(PermissionError):
        union.execute(PurePosixPath("p2"), "echo hi")
