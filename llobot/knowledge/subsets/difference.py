"""
A subset that is a difference of two other subsets.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class DifferenceSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that are in the first subset but not in the second.

    This corresponds to the `-` operator between two `KnowledgeSubset` objects.
    """
    _minuend: KnowledgeSubset
    _subtrahend: KnowledgeSubset

    def __init__(self, minuend: KnowledgeSubset, subtrahend: KnowledgeSubset):
        """
        Creates a new difference subset.

        Args:
            minuend: The subset to subtract from.
            subtrahend: The subset to subtract.
        """
        self._minuend = minuend
        self._subtrahend = subtrahend

    def contains(self, path: Path) -> bool:
        """
        Checks if a path is in the first subset and not in the second.

        Args:
            path: The path to check.

        Returns:
            `True` if `path` is in `minuend` and not in `subtrahend`.
        """
        return self._minuend.contains(path) and not self._subtrahend.contains(path)

__all__ = [
    'DifferenceSubset',
]
