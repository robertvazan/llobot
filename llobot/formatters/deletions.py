from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder, ChatBranch
from llobot.knowledge.indexes import KnowledgeIndex
import llobot.knowledge.rankings

class DeletionFormatter:
    def render(self, deletions: KnowledgeIndex) -> ChatBranch:
        return ChatBranch()

    def __call__(self, deletions: KnowledgeIndex) -> ChatBranch:
        return self.render(deletions)

def create(function: Callable[[KnowledgeIndex], ChatBranch]) -> DeletionFormatter:
    class LambdaDeletionFormatter(DeletionFormatter):
        def render(self, deletions: KnowledgeIndex) -> ChatBranch:
            return function(deletions)
    return LambdaDeletionFormatter()

@lru_cache
def granular(pattern: str = '`{}` (removed)', affirmation: str = 'I see.') -> DeletionFormatter:
    def render(deletions: KnowledgeIndex) -> ChatBranch:
        if not deletions:
            return ChatBranch()
        chat = ChatBuilder()
        # We don't care about order. Just use lexicographical ranking for consistency.
        for path in llobot.knowledge.rankings.lexicographical(deletions):
            chat.add(ChatIntent.SYSTEM)
            chat.add(pattern.format(path))
            chat.add(ChatIntent.AFFIRMATION)
            chat.add(affirmation)
        return chat.build()
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
