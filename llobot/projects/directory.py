from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import blacklist_subset, whitelist_subset
from llobot.projects import Project
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem, ProjectLink
from llobot.utils.fs import read_document
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import validate_zone

class DirectoryProject(Project, ValueTypeMixin):
    """
    A project that sources its content from a filesystem directory.
    """
    _directory: Path
    _zones: frozenset[Path]
    _prefix: Path
    _whitelist: KnowledgeSubset
    _blacklist: KnowledgeSubset

    def __init__(
        self,
        directory: Path | str,
        *,
        zones: set[str | Path] | None = None,
        prefix: Path | str | None = None,
        whitelist: KnowledgeSubset | None = None,
        blacklist: KnowledgeSubset | None = None,
    ):
        """
        Initializes a new DirectoryProject.

        Args:
            directory: The path to the project's root directory. It can contain `~`.
            zones: A set of zone identifiers for the project. If `None`, defaults
                   to a single zone matching the project's prefix.
            prefix: The path prefix for all items in the project. If `None`, it
                    defaults to the last component of the directory path.
            whitelist: A custom whitelist subset for this project.
            blacklist: A custom blacklist subset for this project.
        """
        self._directory = Path(directory).expanduser().absolute()
        self._prefix = Path(prefix) if prefix is not None else Path(self._directory.name)
        validate_zone(self._prefix)

        if zones is not None:
            self._zones = frozenset(Path(z) for z in zones)
        else:
            self._zones = frozenset([self._prefix])

        for zone in self._zones:
            validate_zone(zone)

        self._whitelist = whitelist or whitelist_subset()
        self._blacklist = blacklist or blacklist_subset()

    @property
    def zones(self) -> set[Path]:
        return set(self._zones)

    @property
    def prefixes(self) -> set[Path]:
        return {self._prefix}

    def _to_local_path(self, path: Path) -> Path | None:
        """Strips the project prefix from a path. Returns None if path is not under the prefix."""
        try:
            return path.relative_to(self._prefix)
        except ValueError:
            return None

    def items(self, path: Path) -> list[ProjectItem]:
        local_path = self._to_local_path(path)
        if local_path is None:
            return []
        real_path = self._directory / local_path
        if not real_path.is_dir():
            return []

        result = []
        for p in real_path.iterdir():
            item_path = path / p.name
            if p.is_file():
                result.append(ProjectFile(item_path))
            elif p.is_dir():
                result.append(ProjectDirectory(item_path))
            elif p.is_symlink():
                result.append(ProjectLink(item_path, p.readlink()))
        return result

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

    def tracked(self, item: ProjectItem) -> bool:
        if isinstance(item, ProjectFile):
            return item.path in self._whitelist and item.path not in self._blacklist
        if isinstance(item, ProjectDirectory):
            return item.path not in self._blacklist
        return False

__all__ = [
    'DirectoryProject',
]
