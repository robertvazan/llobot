from __future__ import annotations
from pathlib import Path, PurePosixPath
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import blacklist_subset, whitelist_subset
from llobot.projects import Project
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem, ProjectLink
from llobot.utils.fs import create_parents, read_document, write_text
from llobot.utils.values import ValueTypeMixin
from llobot.utils.zones import validate_zone

class DirectoryProject(Project, ValueTypeMixin):
    """
    A project that sources its content from a filesystem directory.
    Can be configured to be mutable.
    """
    _directory: Path
    _zones: frozenset[PurePosixPath]
    _prefix: PurePosixPath
    _whitelist: KnowledgeSubset
    _blacklist: KnowledgeSubset
    _mutable: bool

    def __init__(
        self,
        directory: Path | str,
        *,
        zones: set[str | PurePosixPath] | None = None,
        prefix: PurePosixPath | str | None = None,
        whitelist: KnowledgeSubset | None = None,
        blacklist: KnowledgeSubset | None = None,
        mutable: bool = False,
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
            mutable: If `True`, the project allows write operations. Defaults to `False`.
        """
        self._directory = Path(directory).expanduser().absolute()
        self._prefix = PurePosixPath(prefix) if prefix is not None else PurePosixPath(self._directory.name)
        if self._prefix.is_absolute():
            raise ValueError(f"Project prefix must be relative: {self._prefix}")
        validate_zone(self._prefix)

        if zones is not None:
            self._zones = frozenset(PurePosixPath(z) for z in zones)
        else:
            self._zones = frozenset([self._prefix])

        for zone in self._zones:
            if zone.is_absolute():
                raise ValueError(f"Project zone must be relative: {zone}")
            validate_zone(zone)

        self._whitelist = whitelist or whitelist_subset()
        self._blacklist = blacklist or blacklist_subset()
        self._mutable = mutable

    @property
    def zones(self) -> set[PurePosixPath]:
        return set(self._zones)

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return {self._prefix}

    def _to_local_path(self, path: PurePosixPath) -> PurePosixPath | None:
        """Strips the project prefix from a path. Returns None if path is not under the prefix."""
        try:
            return path.relative_to(self._prefix)
        except ValueError:
            return None

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
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
                result.append(ProjectLink(item_path, PurePosixPath(p.readlink())))
        return result

    def read(self, path: PurePosixPath) -> str | None:
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

    def mutable(self, path: PurePosixPath) -> bool:
        """
        Checks if the path is mutable.

        A path is mutable if the project is configured as mutable and the
        path is within the project's prefix.
        """
        return self._mutable and self._to_local_path(path) is not None

    def write(self, path: PurePosixPath, content: str):
        """
        Writes content to a file in the project directory.

        Args:
            path: The project path of the file to write.
            content: The content to write.

        Raises:
            PermissionError: If the project is not mutable or the path is
                             outside the project prefix.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable in this project: {path}")
        local_path = self._to_local_path(path)
        # This should not happen if mutable() check passed
        assert local_path, f"Path {path} is not under project prefix despite mutable() check passing"
        real_path = self._directory / local_path
        write_text(real_path, content)

    def remove(self, path: PurePosixPath):
        """
        Removes a file from the project directory.

        Args:
            path: The project path of the file to remove.

        Raises:
            PermissionError: If the project is not mutable or the path is
                             outside the project prefix.
            FileNotFoundError: If the path does not exist.
            IsADirectoryError: If the path is a directory.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable in this project: {path}")
        local_path = self._to_local_path(path)
        # This should not happen if mutable() check passed
        assert local_path, f"Path {path} is not under project prefix despite mutable() check passing"
        real_path = self._directory / local_path
        real_path.unlink()

    def move(self, source: PurePosixPath, destination: PurePosixPath):
        """
        Moves a file within the project directory using a filesystem move.

        Args:
            source: The project path of the file to move.
            destination: The new project path for the file.

        Raises:
            PermissionError: If the project is not mutable or if either path
                             is outside the project prefix.
            FileNotFoundError: If the source file does not exist.
        """
        if not self.mutable(source):
            raise PermissionError(f"Source path is not mutable in this project: {source}")
        if not self.mutable(destination):
            raise PermissionError(f"Destination path is not mutable in this project: {destination}")

        source_local = self._to_local_path(source)
        dest_local = self._to_local_path(destination)
        # This should not happen if mutable() check passed
        assert source_local, f"Path {source} is not under project prefix despite mutable() check passing"
        assert dest_local, f"Path {destination} is not under project prefix despite mutable() check passing"

        real_source = self._directory / source_local
        real_dest = self._directory / dest_local

        create_parents(real_dest)
        real_source.rename(real_dest)

__all__ = [
    'DirectoryProject',
]
