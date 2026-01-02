"""
A project wrapper that exposes only files directly under prefixes.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.projects import Project
from llobot.projects.items import ProjectItem
from llobot.utils.values import ValueTypeMixin

class ShallowProject(Project, ValueTypeMixin):
    """
    A wrapper for another project that restricts access to only items
    directly under the project's prefixes. Subdirectories are listed but
    not traversed.
    """
    _project: Project

    def __init__(self, project: Project):
        """
        Initializes a new ShallowProject.

        Args:
            project: The underlying project to wrap.
        """
        self._project = project

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return self._project.prefixes

    @property
    def summary(self) -> list[str]:
        return [f"{s}, top directory only" for s in self._project.summary]

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
        """
        Returns a list of items if the path is a prefix.

        Only items directly under the prefix are returned. Returns an empty
        list for paths that are not project prefixes.
        """
        if path in self.prefixes:
            return self._project.items(path)
        return []

    def _is_shallow_file(self, path: PurePosixPath) -> bool:
        """Checks if a file path is directly under a project prefix."""
        return path.parent in self.prefixes

    def read(self, path: PurePosixPath) -> str | None:
        """Reads a file if it is directly under a project prefix."""
        if self._is_shallow_file(path):
            return self._project.read(path)
        return None

    def tracked(self, item: ProjectItem) -> bool:
        """
        Checks if an item is tracked.

        An item is tracked if it's a file directly under a prefix and the
        underlying project tracks it. Directories are never tracked in a
        shallow project to prevent recursion in `read_all()`.
        """
        return self._is_shallow_file(item.path) and self._project.tracked(item)

    def mutable(self, path: PurePosixPath) -> bool:
        """
        Checks if a path is mutable and directly under a project prefix.
        """
        return self._is_shallow_file(path) and self._project.mutable(path)

    def write(self, path: PurePosixPath, content: str):
        """
        Writes to a file if it is directly under a project prefix.

        Raises:
            PermissionError: If the path is not shallow (not directly under a prefix).
                             Mutability is checked by the underlying project.
        """
        if not self._is_shallow_file(path):
            raise PermissionError(f"Path is not shallow: {path}")
        self._project.write(path, content)

    def remove(self, path: PurePosixPath):
        """
        Removes a file if it is directly under a project prefix.

        Raises:
            PermissionError: If the path is not shallow (not directly under a prefix).
                             Mutability is checked by the underlying project.
        """
        if not self._is_shallow_file(path):
            raise PermissionError(f"Path is not shallow: {path}")
        self._project.remove(path)

__all__ = [
    'ShallowProject',
]
