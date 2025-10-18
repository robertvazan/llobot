"""
Crammers for formatting and including file indexes.
"""
from __future__ import annotations
from functools import cache
from llobot.chats.builder import ChatBuilder
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

class IndexCrammer:
    """
    Base class for crammers that format and add file indexes to the context.

    An index crammer decides whether to include a file index in the prompt
    based on the available budget in a `ChatBuilder`.
    """

    def cram(self, builder: ChatBuilder, knowledge: Knowledge) -> KnowledgeIndex:
        """
        Adds a knowledge index to the builder if it fits the budget.

        Args:
            builder: The chat builder to add the index to.
            knowledge: The knowledge base to create an index from.

        Returns:
            A `KnowledgeIndex` of the files included in the index.
        """
        raise NotImplementedError

@cache
def standard_index_crammer() -> IndexCrammer:
    """
    Returns the standard index crammer.
    """
    from llobot.crammers.index.optional import OptionalIndexCrammer
    return OptionalIndexCrammer()

__all__ = [
    'IndexCrammer',
    'standard_index_crammer',
]
