"""
A subset that inverts the logic of another subset.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class ComplementSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset that contains all paths not in the original subset.

    This corresponds to the `~` operator on a `KnowledgeSubset`.
    """
    _subset: KnowledgeSubset

    def __init__(self, subset: KnowledgeSubset):
        """
        Creates a new complementary subset.

        Args:
            subset: The subset to invert.
        """
        self._subset = subset

    def contains(self, path: Path) -> bool:
        """
        Checks if the path is NOT in the original subset.

        Args:
            path: The path to check.

        Returns:
            `True` if the path is not in the original subset, `False` otherwise.
        """
        return not self._subset.contains(path)

__all__ = [
    'ComplementSubset',
]
