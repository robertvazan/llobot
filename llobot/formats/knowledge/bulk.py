"""
Bulk knowledge format.
"""
from __future__ import annotations
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking, standard_ranking
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.knowledge import KnowledgeFormat
from llobot.utils.values import ValueTypeMixin

class BulkKnowledgeFormat(KnowledgeFormat, ValueTypeMixin):
    """
    A knowledge format that puts all documents into a single system message.
    """
    _document_format: DocumentFormat

    def __init__(self, document_format: DocumentFormat = standard_document_format()):
        """
        Creates a new bulk knowledge format.

        Args:
            document_format: The format for individual documents.
        """
        self._document_format = document_format

    @property
    def document_format(self) -> DocumentFormat:
        """The format used for rendering individual documents."""
        return self._document_format

    def render_chat(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatThread:
        """
        Renders a knowledge base into a single system message.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            A chat thread with all documents in one system message.
        """
        if ranking is None:
            ranking = standard_ranking(knowledge)

        rendered = self.render(knowledge, ranking)
        if not rendered:
            return ChatThread()

        return ChatThread([ChatMessage(ChatIntent.SYSTEM, rendered)])

__all__ = [
    'BulkKnowledgeFormat',
]
