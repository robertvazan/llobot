"""
Knowledge base for selected project.
"""
from __future__ import annotations
from functools import cached_property
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

class KnowledgeEnv:
    """
    An environment component that holds the project's knowledge.
    """
    _knowledge: Knowledge | None = None

    def set(self, knowledge: Knowledge):
        """
        Sets the project's knowledge.
        """
        self._knowledge = knowledge
        # Bust the index cache if it exists.
        if hasattr(self, '_index'):
            del self._index

    def get(self) -> Knowledge:
        """
        Gets the project's knowledge.

        Returns:
            The project's knowledge, or empty knowledge if not set.
        """
        return self._knowledge or Knowledge()

    @cached_property
    def _index(self) -> KnowledgeIndex:
        return self.get().keys()

    def index(self) -> KnowledgeIndex:
        """
        Gets the index of the project's knowledge.

        Returns:
            The knowledge index.
        """
        return self._index

__all__ = [
    'KnowledgeEnv',
]
