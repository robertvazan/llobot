"""
Chunked knowledge format.
"""
from __future__ import annotations
from llobot.chats.builder import ChatBuilder
from llobot.chats.thread import ChatThread
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking, standard_ranking
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.knowledge import KnowledgeFormat
from llobot.formats.affirmations import affirmation_turn
from llobot.utils.text import concat_documents
from llobot.utils.values import ValueTypeMixin

class ChunkedKnowledgeFormat(KnowledgeFormat, ValueTypeMixin):
    """
    A knowledge format that groups documents into chunks.
    """
    _document_format: DocumentFormat
    _min_size: int

    def __init__(self,
        document_format: DocumentFormat = standard_document_format(),
        min_size: int = 10000
    ):
        """
        Creates a new chunked knowledge format.

        Args:
            document_format: The format for individual documents.
            min_size: The minimum chunk size in characters.
        """
        self._document_format = document_format
        self._min_size = min_size

    @property
    def document_format(self) -> DocumentFormat:
        """The format used for rendering individual documents."""
        return self._document_format

    def render_chat(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatThread:
        """
        Renders a knowledge base by grouping documents into chunks.

        Each chunk is emitted as a separate system message.

        Args:
            knowledge: The knowledge base to render.
            ranking: An optional ranking to order the documents.

        Returns:
            A chat thread with chunked documents.
        """
        if ranking is None:
            ranking = standard_ranking(knowledge)

        chat = ChatBuilder()
        buffer = []
        size = 0

        for path in ranking:
            if path not in knowledge:
                continue
            content = knowledge[path]
            formatted = self.document_format.render(path, content)
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
    'ChunkedKnowledgeFormat',
]
