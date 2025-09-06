from __future__ import annotations
from pathlib import Path
from llobot.fs import read_document
from llobot.projects import Project
from llobot.knowledge.subsets import KnowledgeSubset

class DirectoryProject(Project):
    """
    A project that sources its content from a filesystem directory.

    By default, the project name is derived from the directory name, and all
    paths within the project are prefixed with the project name.
    """
    _directory: Path
    _name: str
    _prefix: Path
    _whitelist: KnowledgeSubset
    _blacklist: KnowledgeSubset

    def __init__(
        self,
        directory: Path | str,
        name: str | None = None,
        prefix: Path | None = None,
        whitelist: KnowledgeSubset | None = None,
        blacklist: KnowledgeSubset | None = None,
    ):
        """
        Initializes a new DirectoryProject.

        Args:
            directory: The path to the project's root directory.
            name: The name of the project. If None, it is derived from the
                  directory name.
            prefix: The path prefix for all files in the project. If None, it
                    defaults to a path with the project's name. Use `Path('.')`
                    for no prefix.
            whitelist: A custom whitelist for this project.
            blacklist: A custom blacklist for this project.
        """
        self._directory = Path(directory).resolve()
        self._name = name or self._directory.name
        self._prefix = prefix if prefix is not None else Path(self._name)
        self._whitelist = whitelist or super().whitelist
        self._blacklist = blacklist or super().blacklist

    @property
    def name(self) -> str:
        return self._name

    @property
    def whitelist(self) -> KnowledgeSubset:
        return self._whitelist

    @property
    def blacklist(self) -> KnowledgeSubset:
        return self._blacklist

    def _to_local_path(self, path: Path) -> Path | None:
        """Strips the project prefix from a path. Returns None if path is not under the prefix."""
        if self._prefix == Path('.') or path.is_relative_to(self._prefix):
            return path.relative_to(self._prefix) if self._prefix != Path('.') else path
        return None

    def list_files(self, path: Path) -> list[str]:
        local_path = self._to_local_path(path)
        if local_path is None:
            return []
        real_path = self._directory / local_path
        if not real_path.is_dir():
            return []
        return [p.name for p in real_path.iterdir() if p.is_file()]

    def list_subdirs(self, path: Path) -> list[str]:
        local_path = self._to_local_path(path)
        if local_path is not None:
            real_path = self._directory / local_path
            if not real_path.is_dir():
                return []
            return [p.name for p in real_path.iterdir() if p.is_dir()]

        if self._prefix != Path('.') and self._prefix.is_relative_to(path):
            relative_prefix = self._prefix.relative_to(path)
            return [relative_prefix.parts[0]] if relative_prefix.parts else []
        return []

    def read(self, path: Path) -> str | None:
        local_path = self._to_local_path(path)
        if local_path is None:
            return None
        real_path = self._directory / local_path
        if not real_path.is_file():
            return None
        try:
            return read_document(real_path)
        except (ValueError, UnicodeDecodeError):
            return None # e.g. binary file

__all__ = [
    'DirectoryProject',
]
