"""
Knowledge base for selected project.
"""
from __future__ import annotations
from functools import cached_property
from llobot.environments import EnvBase
from llobot.environments.projects import ProjectEnv
from llobot.environments.cutoffs import CutoffEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

class KnowledgeEnv(EnvBase):
    """
    An environment component that holds the project's knowledge.
    """
    @cached_property
    def _knowledge(self) -> Knowledge:
        project = self.env[ProjectEnv].get()
        if project:
            cutoff = self.env[CutoffEnv].get()
            return project.knowledge(cutoff)
        return Knowledge()

    def get(self) -> Knowledge:
        """
        Gets the project's knowledge at the configured cutoff.

        Returns:
            The project's knowledge, or empty knowledge if no project is selected.
        """
        return self._knowledge

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
