"""
Chunked knowledge delta format.
"""
from __future__ import annotations
from llobot.chats.builders import ChatBuilder
from llobot.chats.branches import ChatBranch
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.formats.deltas.documents import DocumentDeltaFormat, standard_document_delta_format
from llobot.formats.deltas.knowledge import KnowledgeDeltaFormat
from llobot.formats.affirmations import affirmation_turn
from llobot.utils.text import concat_documents
from llobot.utils.values import ValueTypeMixin

class ChunkedKnowledgeDeltaFormat(KnowledgeDeltaFormat, ValueTypeMixin):
    """
    A knowledge delta format that groups document deltas into chunks.
    """
    _document_delta_format: DocumentDeltaFormat
    _min_size: int

    def __init__(self,
        document_delta_format: DocumentDeltaFormat = standard_document_delta_format(),
        min_size: int = 10000
    ):
        """
        Creates a new chunked knowledge delta format.

        Args:
            document_delta_format: The format for individual document deltas.
            min_size: The minimum chunk size in characters.
        """
        self._document_delta_format = document_delta_format
        self._min_size = min_size

    @property
    def document_delta_format(self) -> DocumentDeltaFormat:
        """The format used for rendering individual document deltas."""
        return self._document_delta_format

    def render_chat(self, delta: KnowledgeDelta) -> ChatBranch:
        """
        Renders a knowledge delta by grouping documents into chunks.

        Each chunk is emitted as a separate system message.

        Args:
            delta: The knowledge delta to render.

        Returns:
            A chat branch with chunked document deltas.
        """
        chat = ChatBuilder()
        buffer = []
        size = 0

        for document in delta:
            formatted = self.document_delta_format.render(document)
            if formatted:
                buffer.append(formatted)
                size += len(formatted)

                # If we've reached the minimum chunk size, emit the chunk
                if size >= self._min_size:
                    chunk = concat_documents(*buffer)
                    chat.add(affirmation_turn(chunk))
                    buffer = []
                    size = 0

        # Handle any remaining items in the last chunk
        if buffer:
            chunk = concat_documents(*buffer)
            chat.add(affirmation_turn(chunk))

        return chat.build()

__all__ = [
    'ChunkedKnowledgeDeltaFormat',
]
