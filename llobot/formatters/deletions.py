from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.contexts import Context
from llobot.formatters.paths import PathFormatter
import llobot.knowledge.rankings
import llobot.contexts
import llobot.contexts.deletions
import llobot.formatters.paths

class DeletionFormatter:
    def render(self, deletions: KnowledgeIndex) -> Context:
        return llobot.contexts.empty()

    def __call__(self, deletions: KnowledgeIndex) -> Context:
        return self.render(deletions)

def create(function: Callable[[KnowledgeIndex], Context]) -> DeletionFormatter:
    class LambdaDeletionFormatter(DeletionFormatter):
        def render(self, deletions: KnowledgeIndex) -> Context:
            return function(deletions)
    return LambdaDeletionFormatter()

@lru_cache
def granular(pattern: PathFormatter = llobot.formatters.paths.pattern('Deleted: `{}`'), affirmation: str = 'I see.') -> DeletionFormatter:
    def render(deletions: KnowledgeIndex) -> Context:
        if not deletions:
            return llobot.contexts.empty()
        parts = []
        # We don't care about order. Just use lexicographical ranking for consistency.
        for path in llobot.knowledge.rankings.lexicographical(deletions):
            chat = ChatBuilder()
            chat.add(ChatIntent.SYSTEM)
            chat.add(pattern(path))
            chat.add(ChatIntent.AFFIRMATION)
            chat.add(affirmation)
            parts.append(llobot.contexts.deletions.annotate(chat.build(), path))
        return llobot.contexts.compose(*parts)
    return create(render)

@cache
def standard() -> DeletionFormatter:
    return granular()

__all__ = [
    'DeletionFormatter',
    'create',
    'granular',
    'standard',
]

