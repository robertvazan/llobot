"""
A subset that matches paths by file suffix.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class SuffixSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that have one of the specified file suffixes.
    """
    _suffixes: frozenset[str]

    def __init__(self, *suffixes: str):
        """
        Creates a new suffix subset.

        Args:
            *suffixes: The file suffixes to match (e.g., '.py', '.txt').
        """
        self._suffixes = frozenset(suffixes)

    def contains(self, path: Path) -> bool:
        """
        Checks if the path's suffix is in the set of specified suffixes.

        Args:
            path: The path to check.

        Returns:
            `True` if the path's suffix matches one of the given suffixes.
        """
        return path.suffix in self._suffixes

__all__ = [
    'SuffixSubset',
]
