from pathlib import Path
from llobot.projects import Project
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset, match_filename, match_suffix

class MockProject(Project):
    def __init__(self, files: dict[str, str | dict]):
        self._files = files
        self._whitelist = super().whitelist
        self._blacklist = super().blacklist

    @property
    def name(self) -> str:
        return "mock"

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

    def list_files(self, path: Path) -> list[str]:
        node = self._get_at(path)
        if isinstance(node, dict):
            return [name for name, content in node.items() if isinstance(content, str)]
        return []

    def list_subdirs(self, path: Path) -> list[str]:
        node = self._get_at(path)
        if isinstance(node, dict):
            return [name for name, content in node.items() if isinstance(content, dict)]
        return []

    def read(self, path: Path) -> str | None:
        content = self._get_at(path)
        return content if isinstance(content, str) else None


def test_project_enumerate_and_load():
    files = {
        "file1.txt": "content1",
        "file2.py": "content2",
        "subdir": {
            "file3.txt": "content3",
            "nested": {
                "file4.py": "content4"
            }
        },
        "blacklisted.txt": "blacklisted"
    }

    project = MockProject(files)
    project.blacklist = match_filename("blacklisted.txt")
    project.whitelist = match_suffix(".txt")

    expected_index = KnowledgeIndex([
        Path("file1.txt"),
        Path("subdir/file3.txt"),
    ])
    assert project.enumerate() == expected_index

    expected_knowledge = Knowledge({
        Path("file1.txt"): "content1",
        Path("subdir/file3.txt"): "content3",
    })
    assert project.load() == expected_knowledge
