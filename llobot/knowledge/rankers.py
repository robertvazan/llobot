from __future__ import annotations
from functools import cache, lru_cache
from llobot.knowledge import Knowledge
from llobot.knowledge.rankings import KnowledgeRanking
import llobot.knowledge.rankings

class KnowledgeRanker:
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        raise NotImplementedError

    def __call__(self, knowledge: Knowledge) -> KnowledgeRanking:
        return self.rank(knowledge)

def create(function: Callable[[Knowledge], KnowledgeRanking]) -> KnowledgeRanker:
    class LambdaKnowledgeRanker(KnowledgeRanker):
        def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
            return function(knowledge)
    return LambdaKnowledgeRanker()

@cache
def lexicographical() -> KnowledgeRanker:
    return create(lambda knowledge: llobot.knowledge.rankings.lexicographical(knowledge))

@cache
def overviews_first(overviews: KnowledgeSubset | None = None) -> KnowledgeRanker:
    return create(lambda knowledge: llobot.knowledge.rankings.overviews_first(knowledge, overviews))

@lru_cache
def ascending(scorer: 'KnowledgeScorer') -> KnowledgeRanker:
    return create(lambda knowledge: llobot.knowledge.rankings.ascending(scorer(knowledge)))

@lru_cache
def descending(scorer: 'KnowledgeScorer') -> KnowledgeRanker:
    return create(lambda knowledge: llobot.knowledge.rankings.descending(scorer(knowledge)))

@cache
def shuffle() -> KnowledgeRanker:
    return create(lambda knowledge: llobot.knowledge.rankings.shuffle(knowledge))

@cache
def standard() -> KnowledgeRanker:
    return overviews_first()

__all__ = [
    'KnowledgeRanker',
    'create',
    'lexicographical',
    'overviews_first',
    'ascending',
    'descending',
    'shuffle',
    'standard',
]
