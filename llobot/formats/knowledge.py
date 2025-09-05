from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats.intents import ChatIntent
from llobot.chats.builders import ChatBuilder
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import KnowledgeDelta, fresh_knowledge_delta
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.formats.deltas import DeltaFormat, standard_delta_format
from llobot.text import concat_documents

class KnowledgeFormat:
    def render(self, delta: KnowledgeDelta) -> ChatBranch:
        return ChatBranch()

    def __call__(self, delta: KnowledgeDelta) -> ChatBranch:
        return self.render(delta)

    def render_fresh(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatBranch:
        delta = fresh_knowledge_delta(knowledge, ranking)
        return self.render(delta)

@lru_cache
def granular_knowledge_format(delta_format: DeltaFormat = standard_delta_format(), affirmation: str = 'I see.') -> KnowledgeFormat:
    class GranularKnowledgeFormat(KnowledgeFormat):
        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            for document in delta:
                formatted = delta_format(document)
                if formatted is not None:
                    chat.add(ChatMessage(ChatIntent.SYSTEM, formatted))
                    chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
            return chat.build()

    return GranularKnowledgeFormat()

@lru_cache
def chunked_knowledge_format(
    delta_format: DeltaFormat = standard_delta_format(),
    affirmation: str = 'I see.',
    min_size: int = 10000
) -> KnowledgeFormat:
    class ChunkedKnowledgeFormat(KnowledgeFormat):
        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            buffer = []
            size = 0

            for document in delta:
                formatted = delta_format(document)
                if formatted is not None:
                    buffer.append(formatted)
                    size += len(formatted)

                    # If we've reached the minimum chunk size, emit the chunk
                    if size >= min_size:
                        chunk = concat_documents(*buffer)
                        chat.add(ChatMessage(ChatIntent.SYSTEM, chunk))
                        chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
                        buffer = []
                        size = 0

            # Handle any remaining items in the last chunk
            if buffer:
                chunk = concat_documents(*buffer)
                chat.add(ChatMessage(ChatIntent.SYSTEM, chunk))
                chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))

            return chat.build()

    return ChunkedKnowledgeFormat()

@cache
def standard_knowledge_format() -> KnowledgeFormat:
    return chunked_knowledge_format()

__all__ = [
    'KnowledgeFormat',
    'granular_knowledge_format',
    'chunked_knowledge_format',
    'standard_knowledge_format',
]
