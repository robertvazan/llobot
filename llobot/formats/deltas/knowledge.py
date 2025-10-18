"""
Knowledge delta format.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.knowledge import KnowledgeDelta, fresh_knowledge_delta
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.formats.deltas.documents import DocumentDeltaFormat
from llobot.utils.text import concat_documents

class KnowledgeDeltaFormat:
    """
    Base class for formats that render `KnowledgeDelta` objects.
    """
    @property
    def document_delta_format(self) -> DocumentDeltaFormat:
        """
        The format used for rendering individual document deltas.
        """
        raise NotImplementedError

    def render(self, delta: KnowledgeDelta) -> str:
        """
        Renders a knowledge delta as a string by concatenating document deltas.

        Args:
            delta: The knowledge delta to render.

        Returns:
            The rendered knowledge delta as a single string.
        """
        return concat_documents(*(self.document_delta_format.render(d) for d in delta))

    def render_chat(self, delta: KnowledgeDelta) -> ChatThread:
        """
        Renders a knowledge delta as a chat thread.

        Args:
            delta: The knowledge delta to render.

        Returns:
            A `ChatThread` containing the rendered delta.
        """
        raise NotImplementedError

    def render_fresh(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> str:
        """
        Renders a fresh knowledge state as a string.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            The rendered knowledge as a single string.
        """
        delta = fresh_knowledge_delta(knowledge, ranking)
        return self.render(delta)

    def render_fresh_chat(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatThread:
        """
        Renders a fresh knowledge state as a chat thread.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            A `ChatThread` containing the rendered knowledge.
        """
        delta = fresh_knowledge_delta(knowledge, ranking)
        return self.render_chat(delta)

def standard_knowledge_delta_format() -> KnowledgeDeltaFormat:
    """
    Returns the standard knowledge delta format.

    Returns:
        The standard `KnowledgeDeltaFormat`.
    """
    from llobot.formats.deltas.chunked import ChunkedKnowledgeDeltaFormat
    return ChunkedKnowledgeDeltaFormat()

__all__ = [
    'KnowledgeDeltaFormat',
    'standard_knowledge_delta_format',
]
