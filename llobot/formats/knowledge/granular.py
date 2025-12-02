"""
Granular knowledge format.
"""
from __future__ import annotations
from llobot.chats.builder import ChatBuilder
from llobot.chats.thread import ChatThread
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking, standard_ranking
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.knowledge import KnowledgeFormat
from llobot.utils.values import ValueTypeMixin

class GranularKnowledgeFormat(KnowledgeFormat, ValueTypeMixin):
    """
    A knowledge format that renders each document individually.
    """
    _document_format: DocumentFormat

    def __init__(self, document_format: DocumentFormat = standard_document_format()):
        """
        Creates a new granular knowledge format.

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
        Renders a knowledge base by formatting each document individually.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            A chat thread with each document as a separate message turn.
        """
        if ranking is None:
            ranking = standard_ranking(knowledge)

        chat = ChatBuilder()
        for path in ranking:
            if path in knowledge:
                chat.add(self.document_format.render_chat(path, knowledge[path]))
        return chat.build()

__all__ = [
    'GranularKnowledgeFormat',
]
