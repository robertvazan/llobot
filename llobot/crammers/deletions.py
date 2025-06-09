from __future__ import annotations
from functools import cache, lru_cache
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.contexts import Context
from llobot.formatters.deletions import DeletionFormatter
import llobot.contexts
import llobot.formatters.deletions

class DeletionCrammer:
    def cram(self, deletions: KnowledgeIndex, budget: int) -> Context:
        return llobot.contexts.empty()

def create(function: Callable[[KnowledgeIndex, int], Context]) -> DeletionCrammer:
    class LambdaDeletionCrammer(DeletionCrammer):
        def cram(self, deletions: KnowledgeIndex, budget: int) -> Context:
            return function(deletions, budget)
    return LambdaDeletionCrammer()

@lru_cache
def all(*,
    formatter: DeletionFormatter = llobot.formatters.deletions.standard(),
) -> DeletionCrammer:
    def cram(deletions: KnowledgeIndex, budget: int) -> Context:
        output = formatter(deletions)
        if output.cost > budget:
            return llobot.contexts.empty()
        return output
    return create(cram)

@cache
def standard() -> DeletionCrammer:
    return all()

__all__ = [
    'DeletionCrammer',
    'create',
    'all',
    'standard',
]

