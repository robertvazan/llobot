"""
Document retrievals.
"""
from __future__ import annotations
from pathlib import Path
from llobot.knowledge.indexes import KnowledgeIndex

class RetrievalsEnv:
    """
    An environment component that holds a set of paths for documents to be retrieved.
    """
    _paths: set[Path]

    def __init__(self):
        self._paths = set()

    def add(self, path: Path):
        """
        Adds a path to the set of retrieved documents.

        Args:
            path: The path to add.
        """
        self._paths.add(path)

    def get(self) -> KnowledgeIndex:
        """
        Gets the set of retrieved documents.

        Returns:
            A `KnowledgeIndex` of the retrieved paths.
        """
        return KnowledgeIndex(self._paths)

    def clear(self):
        """
        Clears all paths from the set of retrieved documents.
        """
        self._paths.clear()

__all__ = [
    'RetrievalsEnv',
]
