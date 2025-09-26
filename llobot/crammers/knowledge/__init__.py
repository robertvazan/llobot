"""
Crammers for selecting knowledge documents.
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
    from llobot.crammers.knowledge.prioritized import PrioritizedKnowledgeCrammer
    return PrioritizedKnowledgeCrammer()

__all__ = [
    'KnowledgeCrammer',
    'standard_knowledge_crammer',
]
