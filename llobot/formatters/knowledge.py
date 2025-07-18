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
            for doc_delta in delta:
                formatted_doc = envelopes(doc_delta)
                if formatted_doc is not None:
                    chat.add(ChatIntent.SYSTEM.message(formatted_doc))
                    chat.add(ChatIntent.AFFIRMATION.message(affirmation))
            return chat.build()

    return GranularKnowledgeFormatter()

@cache
def standard() -> KnowledgeFormatter:
    return granular()

__all__ = [
    'KnowledgeFormatter',
    'standard',
]
