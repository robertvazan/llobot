"""
A subset that matches paths by filename.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class FilenameSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that have one of the specified filenames.
    """
    _names: frozenset[str]

    def __init__(self, *names: str):
        """
        Creates a new filename subset.

        Args:
            *names: The filenames to match.
        """
        self._names = frozenset(names)

    def contains(self, path: Path) -> bool:
        """
        Checks if the path's filename is in the set of specified names.

        Args:
            path: The path to check.

        Returns:
            `True` if the path's name matches one of the given filenames.
        """
        return path.name in self._names

__all__ = [
    'FilenameSubset',
]
