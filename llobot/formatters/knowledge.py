from __future__ import annotations
from functools import cache, lru_cache
import itertools
from llobot.chats import ChatIntent, ChatBuilder
from llobot.knowledge import Knowledge
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.contexts import Context
from llobot.formatters.decorators import Decorator
from llobot.formatters.languages import LanguageGuesser
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.text
import llobot.knowledge.indexes
import llobot.scores.knowledge
import llobot.contexts
import llobot.contexts.documents
import llobot.formatters.languages
import llobot.formatters.decorators
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
def amalgamated(*,
    guesser: LanguageGuesser = llobot.formatters.languages.standard(),
    decorator: Decorator = llobot.formatters.decorators.minimal(),
    inline_markdown: bool = True,
    affirmation: str = 'I see.',
    note: str = '',
) -> KnowledgeFormatter:
    def quote(language: str, documents: list[str]) -> str:
        amalgamated = llobot.text.concat(*documents)
        if language == 'markdown' and inline_markdown:
            return amalgamated
        else:
            return llobot.formatters.envelopes.quote(language, amalgamated)
    def render(knowledge: Knowledge, ranking: KnowledgeRanking) -> Context:
        knowledge &= ranking
        if not knowledge:
            return llobot.contexts.empty()
        decorated = Knowledge({path: decorator(path, content, note) for path, content in knowledge})
        resolved = [(guesser(path, decorated[path]), decorated[path]) for path in ranking if path in decorated]
        blocks = [quote(lang, [document for _, document in group]) for lang, group in itertools.groupby(resolved, key=lambda pair: pair[0])]
        message = llobot.text.concat(*blocks)
        chat = ChatBuilder()
        chat.add(ChatIntent.SYSTEM)
        chat.add(message)
        chat.add(ChatIntent.AFFIRMATION)
        chat.add(affirmation)
        # Compute lengths from decorated documents while exposing original documents via annotation.
        cost = llobot.scores.knowledge.normalize(llobot.scores.knowledge.length(decorated), chat.cost)
        return llobot.contexts.documents.bulk(chat.build(), knowledge, cost)
    return create(render)

@lru_cache
def bulk(envelope: EnvelopeFormatter = llobot.formatters.envelopes.standard(), affirmation: str = 'I see.', note: str = '') -> KnowledgeFormatter:
    def render(knowledge: Knowledge, ranking: KnowledgeRanking) -> Context:
        knowledge &= ranking
        if not knowledge:
            return llobot.contexts.empty()
        blocks = knowledge.transform(lambda path, content: envelope(path, content, note))
        chat = ChatBuilder()
        chat.add(ChatIntent.SYSTEM)
        chat.add(llobot.text.concat(*[blocks[path] for path in ranking if path in blocks]))
        chat.add(ChatIntent.AFFIRMATION)
        chat.add(affirmation)
        cost = llobot.scores.knowledge.normalize(llobot.scores.knowledge.length(blocks), chat.cost)
        return llobot.contexts.documents.bulk(chat.build(), knowledge, cost)
    return create(render)

@lru_cache
def chunked(envelope: EnvelopeFormatter = llobot.formatters.envelopes.standard(), affirmation: str = 'I see.', note: str = '') -> KnowledgeFormatter:
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
    return chunked()

@cache
def updates() -> KnowledgeFormatter:
    return chunked(note='modified')

__all__ = [
    'KnowledgeFormatter',
    'create',
    'amalgamated',
    'bulk',
    'chunked',
    'standard',
    'updates',
]

