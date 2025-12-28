"""
Formats for rendering `Knowledge` objects.

This package provides formatters that can serialize `Knowledge` objects into a
human-readable text format suitable for including in LLM prompts.

Submodules
----------
bulk
    An implementation of `KnowledgeFormat` that puts all documents into a single message.
granular
    An implementation of `KnowledgeFormat` that renders each document individually.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking, standard_ranking
from llobot.formats.documents import DocumentFormat
from llobot.utils.text import concat_documents

class KnowledgeFormat:
    """
    Base class for formats that render `Knowledge` objects.
    """
    @property
    def document_format(self) -> DocumentFormat:
        """
        The format used for rendering individual documents.
        """
        raise NotImplementedError

    def render(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> str:
        """
        Renders a knowledge base as a string by concatenating documents.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            The rendered knowledge base as a single string.
        """
        if ranking is None:
            ranking = standard_ranking(knowledge)
        return concat_documents(*(self.document_format.render(path, knowledge[path]) for path in ranking if path in knowledge))

    def render_chat(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatThread:
        """
        Renders a knowledge base as a chat thread.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            A `ChatThread` containing the rendered knowledge.
        """
        raise NotImplementedError

def standard_knowledge_format() -> KnowledgeFormat:
    """
    Returns the standard knowledge format.

    Returns:
        The standard `KnowledgeFormat`.
    """
    from llobot.formats.knowledge.bulk import BulkKnowledgeFormat
    return BulkKnowledgeFormat()

__all__ = [
    'KnowledgeFormat',
    'standard_knowledge_format',
]
