"""
An empty subset that contains no paths.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class EmptySubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset that contains no paths. It is a singleton-by-value.
    """

    def contains(self, path: PurePosixPath) -> bool:
        """
        Always returns `False`.

        Args:
            path: The path to check.

        Returns:
            `False`.
        """
        return False

__all__ = [
    'EmptySubset',
]
