"""
A universal subset that contains all paths.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class UniversalSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset that contains all paths. It is a singleton-by-value.
    """

    def contains(self, path: PurePosixPath) -> bool:
        """
        Always returns `True`.

        Args:
            path: The path to check.

        Returns:
            `True`.
        """
        return True

__all__ = [
    'UniversalSubset',
]
