"""
Project item types.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin

class ProjectItem:
    """
    Abstract base class for items (files, directories, links) in a project.
    """
    @property
    def path(self) -> Path:
        """
        The path of the item within the project.
        """
        raise NotImplementedError

class ProjectFile(ProjectItem, ValueTypeMixin):
    """
    Represents a file within a project.
    """
    _path: Path

    def __init__(self, path: Path):
        """
        Initializes a new project file.

        Args:
            path: The path of the file within the project.
        """
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

class ProjectDirectory(ProjectItem, ValueTypeMixin):
    """
    Represents a directory within a project.
    """
    _path: Path

    def __init__(self, path: Path):
        """
        Initializes a new project directory.

        Args:
            path: The path of the directory within the project.
        """
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

class ProjectLink(ProjectItem, ValueTypeMixin):
    """
    Represents a symbolic link within a project.
    """
    _path: Path
    _target: Path

    def __init__(self, path: Path, target: Path):
        """
        Initializes a new project link.

        Args:
            path: The path of the link within the project.
            target: The target path of the link.
        """
        self._path = path
        self._target = target

    @property
    def path(self) -> Path:
        return self._path

    @property
    def target(self) -> Path:
        """
        The target path of the link.
        """
        return self._target

__all__ = [
    'ProjectItem',
    'ProjectFile',
    'ProjectDirectory',
    'ProjectLink',
]
