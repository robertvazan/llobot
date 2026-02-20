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
marker
    A project that has one or more prefixes (markers) but no content.
directory
    A project that sources its content from a filesystem directory.
union
    A project that is a union of multiple projects.
items
    Defines item types that can be part of a project (file, directory, link).
"""
from __future__ import annotations
from pathlib import Path, PurePosixPath
from typing import Iterable
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem


class Project:
    """
    A repository of documents that can be enumerated and read. Projects can
    also be mutable, allowing for file modifications. All project implementations
    must be value-comparable (e.g. by inheriting from `ValueTypeMixin`).
    """
    @property
    def prefixes(self) -> set[PurePosixPath]:
        """
        A set of relative path prefixes that define the project's content scope.

        Prefixes must be valid relative paths as per `validate_zone`.
        """
        return set()

    @property
    def summary(self) -> list[str]:
        """
        Returns a list of single-line Markdown descriptions of the project.
        Descriptions should be plain text and not include list markers.
        """
        return []

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
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

    def read(self, path: PurePosixPath) -> str | None:
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

    def walk(self, directory: PurePosixPath | None = None) -> Iterable[ProjectItem]:
        """
        Recursively walks the project to find all items.

        It yields items in a consistent order (sorted by path). It does not
        descend into untracked directories.

        Args:
            directory: The directory to start walking from. If None, walks
                       from all prefixes.
        """
        if directory is None:
            for prefix in sorted(list(self.prefixes)):
                yield from self.walk(prefix)
            return

        # Sort items for consistent order
        sorted_items = sorted(self.items(directory), key=lambda i: i.path)

        for item in sorted_items:
            yield item
            if isinstance(item, ProjectDirectory) and self.tracked(item):
                yield from self.walk(item.path)

    def index(self) -> KnowledgeIndex:
        """
        Returns a KnowledgeIndex of all tracked files in the project.
        """
        from llobot.knowledge.indexes import KnowledgeIndex
        files = []
        for item in self.walk():
            if isinstance(item, ProjectFile) and self.tracked(item):
                files.append(item.path)
        return KnowledgeIndex(files)

    def read_all(self) -> Knowledge:
        """
        Reads all tracked files and returns them as a Knowledge object.
        """
        docs = {}
        for item in self.walk():
            if isinstance(item, ProjectFile) and self.tracked(item):
                content = self.read(item.path)
                if content is not None:
                    docs[item.path] = content
        return Knowledge(docs)

    def __or__(self, other: Project) -> Project:
        """
        Creates a union of this project and another project.
        """
        from llobot.projects.union import union_project
        return union_project(self, other)

    def mutable(self, path: PurePosixPath) -> bool:
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

    def write(self, path: PurePosixPath, content: str) -> None:
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
            raise PermissionError(f"Path is not mutable: ~/{path}")
        raise NotImplementedError(f"Project type {self.__class__.__name__} does not support writing.")

    def remove(self, path: PurePosixPath) -> None:
        """
        Removes a file at the given path.

        Args:
            path: The path of the file to remove.

        Raises:
            PermissionError: If the path is not mutable.
            NotImplementedError: If the project type does not support removing files.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable: ~/{path}")
        raise NotImplementedError(f"Project type {self.__class__.__name__} does not support removing files.")

    def move(self, source: PurePosixPath, destination: PurePosixPath) -> None:
        """
        Moves a file from a source path to a destination path.

        The base implementation uses a read-write-remove sequence, which can
        work across different member projects in a `UnionProject`. Subclasses
        may override this for more efficient, in-project moves that preserve
        file attributes.

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
            raise FileNotFoundError(f"Source file not found or is not a file: ~/{source}")
        if not self.mutable(destination):
            raise PermissionError(f"Destination path is not mutable for writing: ~/{destination}")
        if not self.mutable(source):
            raise PermissionError(f"Source path is not mutable for removal: ~/{source}")

        self.write(destination, content)
        self.remove(source)

    def executable(self, path: PurePosixPath) -> bool:
        """
        Checks whether the given path can be used as a working directory for execution.

        Args:
            path: The path to check.

        Returns:
            `True` if execution is allowed in this path, `False` otherwise.
        """
        return False

    def execute(self, path: PurePosixPath, script: str) -> str:
        """
        Executes a script in the context of the project at the given path.

        The script is executed with the current working directory set to the
        resolved filesystem path corresponding to the given project path.

        Args:
            path: The working directory for the script (project-internal path).
            script: The script content to execute (Linux shell).

        Returns:
            The standard output of the script (combined with standard error).
            Implementations should append the exit code to the output and must
            not raise an exception solely because the exit code is non-zero.

        Raises:
            PermissionError: If the path is not allowed for execution.
            NotImplementedError: If the project type does not support execution.
        """
        if not self.executable(path):
            raise PermissionError(f"Path is not allowed for execution: ~/{path}")
        raise NotImplementedError(f"Project type {self.__class__.__name__} does not support execution.")

type ProjectPrecursor = Project | PurePosixPath | Path | str

def coerce_project(precursor: ProjectPrecursor) -> Project:
    """
    Coerces a precursor into a `Project`.

    - `Project` is returned as is.
    - `Path` is coerced to `DirectoryProject`.
    - `str` starting with `/` or `~` is coerced to `DirectoryProject`.
    - Other `str` values are coerced to `MarkerProject`.
    - `PurePosixPath` is coerced to `MarkerProject`.

    Args:
        precursor: The object to coerce. Can be a `Project`, `Path`, `PurePosixPath`, or `str`.

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
        from llobot.projects.marker import MarkerProject
        return MarkerProject(precursor)
    if isinstance(precursor, PurePosixPath):
        from llobot.projects.marker import MarkerProject
        return MarkerProject(precursor)
    raise TypeError(f"Cannot coerce {precursor} to Project")

__all__ = [
    'Project',
    'ProjectPrecursor',
    'coerce_project',
]
