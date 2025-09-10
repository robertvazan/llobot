"""
Subsets that match paths against glob-like patterns.
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset

class PatternSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that fully match a glob-like pattern.

    This subset is for complex patterns that might contain `**` or are
    absolute. It uses `pathlib.Path.full_match` for matching, which supports
    `*`, `?`, `[]`, and `**` against the entire path string.
    """
    _pattern: str

    def __init__(self, pattern: str):
        """
        Creates a new pattern subset.

        Args:
            pattern: The glob pattern to match against the whole path.
        """
        self._pattern = pattern

    def contains(self, path: Path) -> bool:
        """
        Checks if the path fully matches the pattern.

        Args:
            path: The path to check.

        Returns:
            `True` if the entire path matches the pattern.
        """
        return path.full_match(self._pattern)


class SimplePatternSubset(KnowledgeSubset, ValueTypeMixin):
    """
    A subset containing paths that match a simple, relative glob-like pattern.

    This uses `pathlib.Path.match` for matching, which is suitable for simple
    patterns that do not start with `/` and do not contain `**`. For example,
    `*.py` or `docs/*.md`.
    """
    _pattern: str

    def __init__(self, pattern: str):
        """
        Creates a new simple pattern subset.

        Args:
            pattern: The simple glob pattern to match against.
        """
        self._pattern = pattern

    def contains(self, path: Path) -> bool:
        """
        Checks if the path matches the pattern using `path.match`.

        Args:
            path: The path to check.

        Returns:
            `True` if the path matches the pattern.
        """
        return path.match(self._pattern)


__all__ = [
    'PatternSubset',
    'SimplePatternSubset',
]
