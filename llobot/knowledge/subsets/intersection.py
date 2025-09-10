"""
A subset that is an intersection of two other subsets.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class IntersectionSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that are present in both of two other subsets.

    This corresponds to the `&` operator between two `KnowledgeSubset` objects.
    It flattens nested intersections for efficiency.
    """
    _subsets: tuple[KnowledgeSubset, ...]

    def __init__(self, *subsets: KnowledgeSubset):
        """
        Creates a new intersection subset.

        Args:
            *subsets: The subsets to intersect.
        """
        flattened = []
        for subset in subsets:
            if isinstance(subset, IntersectionSubset):
                flattened.extend(subset._subsets)
            else:
                flattened.append(subset)
        self._subsets = tuple(flattened)

    def contains(self, path: Path) -> bool:
        """
        Checks if a path is in all of the component subsets.

        Args:
            path: The path to check.

        Returns:
            `True` if the path is in all subsets, `False` otherwise.
        """
        return all(subset.contains(path) for subset in self._subsets)

__all__ = [
    'IntersectionSubset',
]
