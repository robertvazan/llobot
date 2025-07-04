from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder
from llobot.knowledge import Knowledge
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.contexts import Context
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.text
import llobot.contexts
import llobot.contexts.documents
import llobot.formatters.envelopes

class KnowledgeFormatter:
    # The knowledge we receive is likely trimmed. We cannot compute ranking from it ourselves, so we take it as a parameter.
    def render(self, knowledge: Knowledge, ranking: KnowledgeRanking) -> Context:
        return llobot.contexts.empty()

    def __call__(self, knowledge: Knowledge, ranking: KnowledgeRanking) -> Context:
        return self.render(knowledge, ranking)

def create(function: Callable[[Knowledge, KnowledgeRanking], Context]) -> KnowledgeFormatter:
    class LambdaKnowledgeFormatter(KnowledgeFormatter):
        def render(self, knowledge: Knowledge, ranking: KnowledgeRanking) -> Context:
            return function(knowledge, ranking)
    return LambdaKnowledgeFormatter()

@lru_cache
def granular(envelope: EnvelopeFormatter = llobot.formatters.envelopes.standard(), affirmation: str = 'I see.', note: str = '') -> KnowledgeFormatter:
    def render(knowledge: Knowledge, ranking: KnowledgeRanking) -> Context:
        knowledge &= ranking
        parts = []
        for path in ranking:
            if path in knowledge:
                chat = ChatBuilder()
                chat.add(ChatIntent.SYSTEM)
                chat.add(envelope(path, knowledge[path], note))
                chat.add(ChatIntent.AFFIRMATION)
                chat.add(affirmation)
                parts.append(llobot.contexts.documents.annotate(chat.build(), path, knowledge[path]))
        return llobot.contexts.compose(*parts)
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

