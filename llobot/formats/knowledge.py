from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats.intents import ChatIntent
from llobot.chats.builders import ChatBuilder
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.knowledge import KnowledgeDelta, fresh_knowledge_delta
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.affirmations import affirmation_turn
from llobot.text import concat_documents

class KnowledgeFormat:
    @property
    def document_format(self) -> DocumentFormat:
        raise NotImplementedError

    def render(self, delta: KnowledgeDelta) -> ChatBranch:
        return ChatBranch()

    def __call__(self, delta: KnowledgeDelta) -> ChatBranch:
        return self.render(delta)

    def render_fresh(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatBranch:
        delta = fresh_knowledge_delta(knowledge, ranking)
        return self.render(delta)

@lru_cache
def granular_knowledge_format(document_format: DocumentFormat = standard_document_format()) -> KnowledgeFormat:
    class GranularKnowledgeFormat(KnowledgeFormat):
        def __init__(self, document_format: DocumentFormat):
            self._document_format = document_format

        @property
        def document_format(self) -> DocumentFormat:
            return self._document_format

        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            for document in delta:
                formatted = self.document_format(document)
                if formatted is not None:
                    chat.add(affirmation_turn(ChatMessage(ChatIntent.SYSTEM, formatted)))
            return chat.build()

    return GranularKnowledgeFormat(document_format)

@lru_cache
def chunked_knowledge_format(
    document_format: DocumentFormat = standard_document_format(),
    min_size: int = 10000
) -> KnowledgeFormat:
    class ChunkedKnowledgeFormat(KnowledgeFormat):
        def __init__(self, document_format: DocumentFormat, min_size: int):
            self._document_format = document_format
            self._min_size = min_size

        @property
        def document_format(self) -> DocumentFormat:
            return self._document_format

        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            buffer = []
            size = 0

            for document in delta:
                formatted = self.document_format(document)
                if formatted is not None:
                    buffer.append(formatted)
                    size += len(formatted)

                    # If we've reached the minimum chunk size, emit the chunk
                    if size >= self._min_size:
                        chunk = concat_documents(*buffer)
                        chat.add(affirmation_turn(ChatMessage(ChatIntent.SYSTEM, chunk)))
                        buffer = []
                        size = 0

            # Handle any remaining items in the last chunk
            if buffer:
                chunk = concat_documents(*buffer)
                chat.add(affirmation_turn(ChatMessage(ChatIntent.SYSTEM, chunk)))

            return chat.build()

    return ChunkedKnowledgeFormat(document_format, min_size)

@cache
def standard_knowledge_format() -> KnowledgeFormat:
    return chunked_knowledge_format()

__all__ = [
    'KnowledgeFormat',
    'granular_knowledge_format',
    'chunked_knowledge_format',
    'standard_knowledge_format',
]
