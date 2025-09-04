from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats.intents import ChatIntent
from llobot.chats.builders import ChatBuilder
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import KnowledgeDelta, fresh_knowledge_delta
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.formatters.envelopes import EnvelopeFormatter, standard_envelopes
from llobot.text import concat_documents

class KnowledgeFormatter:
    def render(self, delta: KnowledgeDelta) -> ChatBranch:
        return ChatBranch()

    def __call__(self, delta: KnowledgeDelta) -> ChatBranch:
        return self.render(delta)

    def render_fresh(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatBranch:
        delta = fresh_knowledge_delta(knowledge, ranking)
        return self.render(delta)

@lru_cache
def granular_knowledge_formatter(envelopes: EnvelopeFormatter = standard_envelopes(), affirmation: str = 'I see.') -> KnowledgeFormatter:
    class GranularKnowledgeFormatter(KnowledgeFormatter):
        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            for document in delta:
                formatted = envelopes(document)
                if formatted is not None:
                    chat.add(ChatMessage(ChatIntent.SYSTEM, formatted))
                    chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
            return chat.build()

    return GranularKnowledgeFormatter()

@lru_cache
def chunked_knowledge_formatter(
    envelopes: EnvelopeFormatter = standard_envelopes(),
    affirmation: str = 'I see.',
    min_size: int = 10000
) -> KnowledgeFormatter:
    class ChunkedKnowledgeFormatter(KnowledgeFormatter):
        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            buffer = []
            size = 0

            for document in delta:
                formatted = envelopes(document)
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

    return ChunkedKnowledgeFormatter()

@cache
def standard_knowledge_formatter() -> KnowledgeFormatter:
    return chunked_knowledge_formatter()

__all__ = [
    'KnowledgeFormatter',
    'granular_knowledge_formatter',
    'chunked_knowledge_formatter',
    'standard_knowledge_formatter',
]
