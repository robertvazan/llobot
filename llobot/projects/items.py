"""
Project item types.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.utils.values import ValueTypeMixin

class ProjectItem:
    """
    Abstract base class for items (files, directories, links) in a project.
    """
    @property
    def path(self) -> PurePosixPath:
        """
        The path of the item within the project.
        """
        raise NotImplementedError

class ProjectFile(ProjectItem, ValueTypeMixin):
    """
    Represents a file within a project.
    """
    _path: PurePosixPath

    def __init__(self, path: PurePosixPath):
        """
        Initializes a new project file.

        Args:
            path: The path of the file within the project.
        """
        self._path = path

    @property
    def path(self) -> PurePosixPath:
        return self._path

class ProjectDirectory(ProjectItem, ValueTypeMixin):
    """
    Represents a directory within a project.
    """
    _path: PurePosixPath

    def __init__(self, path: PurePosixPath):
        """
        Initializes a new project directory.

        Args:
            path: The path of the directory within the project.
        """
        self._path = path

    @property
    def path(self) -> PurePosixPath:
        return self._path

class ProjectLink(ProjectItem, ValueTypeMixin):
    """
    Represents a symbolic link within a project.
    """
    _path: PurePosixPath
    _target: PurePosixPath

    def __init__(self, path: PurePosixPath, target: PurePosixPath):
        """
        Initializes a new project link.

        Args:
            path: The path of the link within the project.
            target: The target path of the link.
        """
        self._path = path
        self._target = target

    @property
    def path(self) -> PurePosixPath:
        return self._path

    @property
    def target(self) -> PurePosixPath:
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
