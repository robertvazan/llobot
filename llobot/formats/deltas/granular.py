"""
Granular knowledge delta format.
"""
from __future__ import annotations
from llobot.chats.builder import ChatBuilder
from llobot.chats.thread import ChatThread
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.formats.deltas.documents import DocumentDeltaFormat, standard_document_delta_format
from llobot.formats.deltas.knowledge import KnowledgeDeltaFormat
from llobot.utils.values import ValueTypeMixin

class GranularKnowledgeDeltaFormat(KnowledgeDeltaFormat, ValueTypeMixin):
    """
    A knowledge delta format that renders each document delta individually.
    """
    _document_delta_format: DocumentDeltaFormat

    def __init__(self, document_delta_format: DocumentDeltaFormat = standard_document_delta_format()):
        """
        Creates a new granular knowledge delta format.

        Args:
            document_delta_format: The format for individual document deltas.
        """
        self._document_delta_format = document_delta_format

    @property
    def document_delta_format(self) -> DocumentDeltaFormat:
        """The format used for rendering individual document deltas."""
        return self._document_delta_format

    def render_chat(self, delta: KnowledgeDelta) -> ChatThread:
        """
        Renders a knowledge delta by formatting each document delta individually.

        Args:
            delta: The knowledge delta to render.

        Returns:
            A chat thread with each document delta as a separate message turn.
        """
        chat = ChatBuilder()
        for document in delta:
            chat.add(self.document_delta_format.render_chat(document))
        return chat.build()

__all__ = [
    'GranularKnowledgeDeltaFormat',
]
