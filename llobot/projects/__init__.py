"""
Projects are repositories of documents that can be enumerated and read.

This package defines the base `Project` class and different implementations for
various project sources.

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
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
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

    def refresh(self, archive: KnowledgeArchive):
        """
        Checks for updates and archives a new snapshot for each prefix if changes are found.

        For each project prefix, a separate snapshot is created in the archive
        under a zone with the same path as the prefix. Paths in the snapshot
        are relative to the prefix.

        Args:
            archive: The knowledge archive to refresh.
        """
        all_knowledge = self.read_all()
        for prefix in self.prefixes:
            knowledge_slice = all_knowledge / prefix
            archive.refresh(prefix, knowledge_slice)

    def last(self, archive: KnowledgeArchive, cutoff: datetime | None = None) -> Knowledge:
        """
        Retrieves the most recent snapshots from the archive for this project.

        For each project prefix, the latest snapshot is retrieved from the
        archive zone corresponding to that prefix. The snapshots are then
        merged into a single `Knowledge` object with paths restored to be
        relative to the project root.

        Args:
            archive: The knowledge archive to retrieve from.
            cutoff: If provided, only snapshots at or before this time are considered.

        Returns:
            The most recent Knowledge object, or an empty one if none are found.
        """
        knowledge = Knowledge()
        for prefix in self.prefixes:
            knowledge_slice = prefix / archive.last(prefix, cutoff)
            knowledge |= knowledge_slice
        return knowledge

    def __or__(self, other: Project) -> Project:
        """
        Creates a union of this project and another project.
        """
        from llobot.projects.union import union_project
        return union_project(self, other)

__all__ = [
    'Project',
]
