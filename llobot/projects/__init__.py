"""
Projects are repositories of documents that can be enumerated and read.

This package defines the base `Project` class and different implementations for
various project sources.

Submodules
----------
dummy
    A dummy project that has a name but no content.
directory
    A project that sources its content from a filesystem directory.
none
    A project that represents the absence of a project.
union
    A project that is a union of multiple projects.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import blacklist_subset, whitelist_subset


class Project:
    """
    A repository of documents that can be enumerated and read.
    """
    @property
    def name(self) -> str:
        """
        Project name.
        """
        raise NotImplementedError

    @property
    def whitelist(self) -> KnowledgeSubset:
        """
        A subset of files to be included in the knowledge base.
        This is only applied to files, not directories.
        """
        return whitelist_subset()

    @property
    def blacklist(self) -> KnowledgeSubset:
        """
        A subset of files and directories to be excluded from the knowledge base.
        """
        return blacklist_subset()

    def list_files(self, path: Path) -> list[str]:
        """
        Returns an unfiltered list of files in a directory.
        """
        return []

    def list_subdirs(self, path: Path) -> list[str]:
        """
        Returns an unfiltered list of subdirectories in a directory.
        """
        return []

    def read(self, path: Path) -> str | None:
        """
        Reads a file if it exists, regardless of filters.
        """
        return None

    def _walk(self, directory: Path) -> 'Iterable[Path]':
        if directory in self.blacklist:
            return
        # Files are sorted to ensure consistent order
        for filename in sorted(self.list_files(directory)):
            path = directory / filename
            if path in self.whitelist and path not in self.blacklist:
                yield path
        # Subdirectories are sorted to ensure consistent order
        for dirname in sorted(self.list_subdirs(directory)):
            yield from self._walk(directory / dirname)

    def enumerate(self) -> KnowledgeIndex:
        """
        Walks the project and returns a knowledge index of all files matching
        the whitelist and not in the blacklist.
        """
        return KnowledgeIndex(self._walk(Path('.')))

    def load(self) -> Knowledge:
        """
        Reads all files returned by enumerate() and returns them as a Knowledge object.
        """
        docs = {}
        for path in self.enumerate():
            content = self.read(path)
            if content is not None:
                docs[path] = content
        return Knowledge(docs)

    def refresh(self, archive: KnowledgeArchive):
        """
        Checks for updates from the source and archives a new snapshot if changes are found.

        Args:
            archive: The knowledge archive to refresh.
        """
        archive.refresh(self.name, self.load())

    def last(self, archive: KnowledgeArchive, cutoff: datetime | None = None) -> Knowledge:
        """
        Retrieves the most recent snapshot from the archive for this project.

        Args:
            archive: The knowledge archive to retrieve from.
            cutoff: If provided, only snapshots at or before this time are considered.

        Returns:
            The most recent Knowledge object, or an empty one if none are found.
        """
        return archive.last(self.name, cutoff)

    def __or__(self, other: Project) -> Project:
        """
        Creates a union of this project and another project.
        """
        from llobot.projects.union import union_project
        return union_project(self, other)

__all__ = [
    'Project',
]
