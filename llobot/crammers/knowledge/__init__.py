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
from llobot.chats.builders import ChatBuilder
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

class KnowledgeCrammer:
    """
    Base class for crammers that select knowledge documents.

    A knowledge crammer selects a subset of documents from a knowledge base
    that fit within the budget of a `ChatBuilder`.
    """
    def cram(self, builder: ChatBuilder, knowledge: Knowledge) -> KnowledgeIndex:
        """
        Selects knowledge documents and adds them to the builder.

        Args:
            builder: The chat builder to add documents to.
            knowledge: The knowledge base to select documents from.

        Returns:
            A `KnowledgeIndex` of the documents that were added.
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
