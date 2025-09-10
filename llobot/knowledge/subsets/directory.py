"""
A subset that matches paths within specified directories.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class DirectorySubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that are within one of the specified directories.

    A path is considered to be in a directory if any of its parent components
    match one of the specified directory names.
    """
    _directories: frozenset[str]

    def __init__(self, *directories: str):
        """
        Creates a new directory subset.

        Args:
            *directories: The names of the directories to match.
        """
        self._directories = frozenset(directories)

    def contains(self, path: Path) -> bool:
        """
        Checks if the path is in any of the specified directories.

        Args:
            path: The path to check.

        Returns:
            `True` if any of the path's components match a directory name.
        """
        return any(part in self._directories for part in path.parts)

__all__ = [
    'DirectorySubset',
]
