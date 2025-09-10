"""
A subset defined by an explicit collection of paths.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex

class PathsSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing an explicit set of paths.

    This is useful for creating subsets from existing `KnowledgeIndex` or
    other collections of paths.
    """
    _paths: KnowledgeIndex

    def __init__(self, paths: KnowledgeIndex):
        """
        Creates a new paths-based subset.

        Args:
            paths: A `KnowledgeIndex` containing the paths for this subset.
        """
        self._paths = paths

    def contains(self, path: Path) -> bool:
        """
        Checks if the path is in the predefined set of paths.

        Args:
            path: The path to check.

        Returns:
            `True` if the path is in the `KnowledgeIndex`.
        """
        return path in self._paths

__all__ = [
    'PathsSubset',
]
