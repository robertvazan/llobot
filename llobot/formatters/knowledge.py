from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder, ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.formatters.envelopes

class KnowledgeFormatter:
    # The knowledge we receive is likely trimmed. We cannot compute ranking from it ourselves, so we take it as a parameter.
    def render(self, knowledge: Knowledge, ranking: KnowledgeRanking) -> ChatBranch:
        return ChatBranch()

    def __call__(self, knowledge: Knowledge, ranking: KnowledgeRanking) -> ChatBranch:
        return self.render(knowledge, ranking)

def create(function: Callable[[Knowledge, KnowledgeRanking], ChatBranch]) -> KnowledgeFormatter:
    class LambdaKnowledgeFormatter(KnowledgeFormatter):
        def render(self, knowledge: Knowledge, ranking: KnowledgeRanking) -> ChatBranch:
            return function(knowledge, ranking)
    return LambdaKnowledgeFormatter()

@lru_cache
def granular(envelope: EnvelopeFormatter = llobot.formatters.envelopes.standard(), affirmation: str = 'I see.', note: str = '') -> KnowledgeFormatter:
    def render(knowledge: Knowledge, ranking: KnowledgeRanking) -> ChatBranch:
        knowledge &= ranking
        chat = ChatBuilder()
        for path in ranking:
            if path in knowledge:
                chat.add(ChatIntent.SYSTEM)
                chat.add(envelope(path, knowledge[path], note))
                chat.add(ChatIntent.AFFIRMATION)
                chat.add(affirmation)
        return chat.build()
    return create(render)

@cache
def standard() -> KnowledgeFormatter:
    return granular()

@cache
def updates() -> KnowledgeFormatter:
    return granular(note='modified')

__all__ = [
    'KnowledgeFormatter',
    'create',
    'granular',
    'standard',
    'updates',
]
