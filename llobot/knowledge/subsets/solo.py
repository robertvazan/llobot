"""
A subset that contains a single path.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class SoloSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset that contains exactly one path.
    """
    _path: PurePosixPath

    def __init__(self, path: PurePosixPath):
        """
        Creates a new solo subset.

        Args:
            path: The single path to be included in the subset.
        """
        self._path = path

    def contains(self, path: PurePosixPath) -> bool:
        """
        Checks if the given path is the one in this subset.

        Args:
            path: The path to check.

        Returns:
            `True` if the path matches the one stored in this subset.
        """
        return self._path == path

__all__ = [
    'SoloSubset',
]
