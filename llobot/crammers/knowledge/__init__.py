"""
Crammers for selecting knowledge documents to fit in a context budget.

This package defines the `KnowledgeCrammer` base class and standard
implementations for selecting a subset of documents from a `Knowledge` base
that will fit within the remaining budget of a `ChatBuilder`.

Submodules
----------
ranked
    `RankedKnowledgeCrammer` that selects documents from a ranked list.
"""
from __future__ import annotations
from functools import cache
from llobot.environments import Environment

class KnowledgeCrammer:
    """
    Base class for crammers that select knowledge documents.

    A knowledge crammer selects a subset of documents from the currently selected
    project that fit within the remaining budget of the context.
    """
    def cram(self, env: Environment) -> None:
        """
        Selects knowledge documents and adds them to the context.

        It pulls knowledge from `ProjectEnv` and updates `KnowledgeEnv` with
        the files that were added to the context.

        Args:
            env: The environment containing context, project, and knowledge state.
        """
        raise NotImplementedError

@cache
def standard_knowledge_crammer() -> KnowledgeCrammer:
    """
    Returns the standard knowledge crammer.
    """
    from llobot.crammers.knowledge.ranked import RankedKnowledgeCrammer
    return RankedKnowledgeCrammer()

__all__ = [
    'KnowledgeCrammer',
    'standard_knowledge_crammer',
]
