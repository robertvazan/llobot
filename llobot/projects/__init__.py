"""
Projects are repositories of documents that can be enumerated and read.

This package defines the base `Project` class and different implementations for
various project sources.

Subpackages
-----------
library
    `ProjectLibrary` for looking up projects by key.

Submodules
----------
empty
    An empty project that has no content.
zone
    A project that only has zones but no content.
directory
    A project that sources its content from a filesystem directory.
union
    A project that is a union of multiple projects.
items
    Defines item types that can be part of a project (file, directory, link).
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem


class Project:
    """
    A repository of documents that can be enumerated and read. Projects can
    also be mutable, allowing for file modifications.
    """
    @property
    def zones(self) -> set[Path]:
        """
        A set of zone identifiers associated with the project.

        Zone identifiers must be valid relative paths as per `validate_zone`.
        """
        return set()

    @property
    def prefixes(self) -> set[Path]:
        """
        A set of relative path prefixes that define the project's content scope.

        Prefixes must be valid relative paths as per `validate_zone`.
        """
        return set()

    def items(self, path: Path) -> list[ProjectItem]:
        """
        Returns a list of items in a directory.

        This method only works for paths that are inside one of the project's
        `prefixes`. It returns an empty list for any path outside all prefixes.

        Args:
            path: The path of the directory within the project.

        Returns:
            A list of `ProjectItem` instances.
        """
        return []

    def read(self, path: Path) -> str | None:
        """
        Reads a file if it exists.

        Args:
            path: The path of the file to read.

        Returns:
            The content of the file, or `None` if it doesn't exist or cannot be read.
        """
        return None

    def tracked(self, item: ProjectItem) -> bool:
        """
        Indicates whether an item should be included in project-derived knowledge.

        Args:
            item: The project item to check.

        Returns:
            `True` if the item is tracked, `False` otherwise.
        """
        return False

    def _walk(self, directory: Path) -> Iterable[ProjectFile]:
        """Recursively walks the project to find all tracked files."""
        # Sort items for consistent order
        sorted_items = sorted(self.items(directory), key=lambda i: i.path)

        for item in sorted_items:
            if self.tracked(item):
                if isinstance(item, ProjectFile):
                    yield item
                elif isinstance(item, ProjectDirectory):
                    yield from self._walk(item.path)

    def read_all(self) -> Knowledge:
        """
        Reads all tracked files and returns them as a Knowledge object.
        """
        docs = {}
        for prefix in self.prefixes:
            for file in self._walk(prefix):
                content = self.read(file.path)
                if content is not None:
                    docs[file.path] = content
        return Knowledge(docs)

    def __or__(self, other: Project) -> Project:
        """
        Creates a union of this project and another project.
        """
        from llobot.projects.union import union_project
        return union_project(self, other)

    def mutable(self, path: Path) -> bool:
        """
        Checks whether the given path is mutable.

        The path does not have to exist. Paths outside of the project's
        prefix(es) are reported as immutable. Whitelist and blacklist are
        not considered.

        Args:
            path: The path to check.

        Returns:
            `True` if the path is mutable, `False` otherwise.
        """
        return False

    def write(self, path: Path, content: str):
        """
        Writes content to a file at the given path.

        Args:
            path: The path of the file to write.
            content: The content to write.

        Raises:
            PermissionError: If the path is not mutable.
            NotImplementedError: If the project type does not support writing.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable: {path}")
        raise NotImplementedError(f"Project type {self.__class__.__name__} does not support writing.")

    def remove(self, path: Path):
        """
        Removes a file at the given path.

        Args:
            path: The path of the file to remove.

        Raises:
            PermissionError: If the path is not mutable.
            NotImplementedError: If the project type does not support removing files.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable: {path}")
        raise NotImplementedError(f"Project type {self.__class__.__name__} does not support removing files.")

    def move(self, source: Path, destination: Path):
        """
        Moves a file from a source path to a destination path.

        This is implemented as a read-write-remove sequence and can work
        across different member projects in a `UnionProject`.

        Args:
            source: The path of the file to move.
            destination: The new path for the file.

        Raises:
            PermissionError: If the source is not readable/removable or the
                             destination is not writable.
            FileNotFoundError: If the source file does not exist or is not a file.
        """
        content = self.read(source)
        if content is None:
            raise FileNotFoundError(f"Source file not found or is not a file: {source}")
        if not self.mutable(destination):
            raise PermissionError(f"Destination path is not mutable for writing: {destination}")
        if not self.mutable(source):
            raise PermissionError(f"Source path is not mutable for removal: {source}")

        self.write(destination, content)
        self.remove(source)

    def update(self, delta: DocumentDelta | KnowledgeDelta):
        """
        Applies a document or knowledge delta to the project.

        Args:
            delta: The delta to apply.
        """
        deltas = [delta] if isinstance(delta, DocumentDelta) else delta
        for d in deltas:
            if d.removed:
                self.remove(d.path)
            elif d.moved_from:
                self.move(d.moved_from, d.path)
            elif d.content is not None:
                self.write(d.path, d.content)
            else:
                # A document delta must represent some change.
                assert False, f"Invalid DocumentDelta with no action: {d}"

type ProjectPrecursor = Project | Path | str

def coerce_project(precursor: ProjectPrecursor) -> Project:
    """
    Coerces a precursor into a `Project`.

    - `Project` is returned as is.
    - `Path` is coerced to `DirectoryProject`.
    - `str` starting with `/` or `~` is coerced to `DirectoryProject`.
    - Other `str` values are coerced to `ZoneProject`.

    Args:
        precursor: The object to coerce. Can be a `Project`, `Path`, or `str`.

    Returns:
        A `Project` instance.
    """
    if isinstance(precursor, Project):
        return precursor
    from llobot.projects.directory import DirectoryProject
    if isinstance(precursor, Path):
        return DirectoryProject(precursor)
    if isinstance(precursor, str):
        if precursor.startswith('/') or precursor.startswith('~'):
            return DirectoryProject(precursor)
        from llobot.projects.zone import ZoneProject
        return ZoneProject(precursor)
    raise TypeError(f"Cannot coerce {precursor} to Project")

__all__ = [
    'Project',
    'ProjectPrecursor',
    'coerce_project',
]
