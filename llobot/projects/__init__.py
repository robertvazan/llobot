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
from llobot.projects.items import ProjectDirectory, ProjectFile, ProjectItem


class Project:
    """
    A repository of documents that can be enumerated and read.
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
