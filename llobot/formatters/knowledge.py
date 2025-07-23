from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder, ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import KnowledgeDelta
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.formatters.envelopes
import llobot.knowledge.rankings
import llobot.knowledge.deltas
import llobot.text

class KnowledgeFormatter:
    def render(self, delta: KnowledgeDelta) -> ChatBranch:
        return ChatBranch()

    def __call__(self, delta: KnowledgeDelta) -> ChatBranch:
        return self.render(delta)

    def render_fresh(self, knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> ChatBranch:
        delta = llobot.knowledge.deltas.fresh(knowledge, ranking)
        return self.render(delta)

@lru_cache
def granular(envelopes: EnvelopeFormatter = llobot.formatters.envelopes.standard(), affirmation: str = 'I see.') -> KnowledgeFormatter:
    class GranularKnowledgeFormatter(KnowledgeFormatter):
        def render(self, delta: KnowledgeDelta) -> ChatBranch:
            chat = ChatBuilder()
            for document in delta:
                formatted = envelopes(document)
                if formatted is not None:
                    chat.add(ChatIntent.SYSTEM.message(formatted))
                    chat.add(ChatIntent.AFFIRMATION.message(affirmation))
            return chat.build()

    return GranularKnowledgeFormatter()

@lru_cache
def chunked(
    envelopes: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
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
                        chunk = llobot.text.concat(*buffer)
                        chat.add(ChatIntent.SYSTEM.message(chunk))
                        chat.add(ChatIntent.AFFIRMATION.message(affirmation))
                        buffer = []
                        size = 0

            # Handle any remaining items in the last chunk
            if buffer:
                chunk = llobot.text.concat(*buffer)
                chat.add(ChatIntent.SYSTEM.message(chunk))
                chat.add(ChatIntent.AFFIRMATION.message(affirmation))

            return chat.build()

    return ChunkedKnowledgeFormatter()

@cache
def standard() -> KnowledgeFormatter:
    return chunked()

__all__ = [
    'KnowledgeFormatter',
    'granular',
    'chunked',
    'standard',
]
