"""
A subset that is a union of other subsets.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class UnionSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that are present in any of the component subsets.

    This corresponds to the `|` operator on `KnowledgeSubset` objects. It
    flattens nested unions for efficiency.
    """
    _subsets: tuple[KnowledgeSubset, ...]

    def __init__(self, *subsets: KnowledgeSubset):
        """
        Creates a new union subset.

        Args:
            *subsets: The subsets to combine.
        """
        flattened = []
        for subset in subsets:
            if isinstance(subset, UnionSubset):
                flattened.extend(subset._subsets)
            else:
                flattened.append(subset)
        self._subsets = tuple(flattened)

    def contains(self, path: Path) -> bool:
        """
        Checks if a path is in any of the component subsets.

        Args:
            path: The path to check.

        Returns:
            `True` if the path is in at least one of the subsets.
        """
        return any(subset.contains(path) for subset in self._subsets)

__all__ = [
    'UnionSubset',
]
