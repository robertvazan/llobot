from __future__ import annotations
from functools import cache, lru_cache
from llobot.knowledge import Knowledge
from llobot.knowledge.rankings import (
    KnowledgeRanking,
    rank_lexicographically,
    rank_overviews_first,
    rank_ascending,
    rank_descending,
    rank_shuffled,
)
from llobot.knowledge.scores.scorers import KnowledgeScorer

class KnowledgeRanker:
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        raise NotImplementedError

    def __call__(self, knowledge: Knowledge) -> KnowledgeRanking:
        return self.rank(knowledge)

def create_ranker(function: Callable[[Knowledge], KnowledgeRanking]) -> KnowledgeRanker:
    class LambdaKnowledgeRanker(KnowledgeRanker):
        def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
            return function(knowledge)
    return LambdaKnowledgeRanker()

@cache
def lexicographical_ranker() -> KnowledgeRanker:
    return create_ranker(lambda knowledge: rank_lexicographically(knowledge))

@cache
def overviews_first_ranker(overviews: KnowledgeSubset | None = None) -> KnowledgeRanker:
    return create_ranker(lambda knowledge: rank_overviews_first(knowledge, overviews))

@lru_cache
def ascending_ranker(scorer: KnowledgeScorer) -> KnowledgeRanker:
    return create_ranker(lambda knowledge: rank_ascending(scorer.score(knowledge)))

@lru_cache
def descending_ranker(scorer: KnowledgeScorer) -> KnowledgeRanker:
    return create_ranker(lambda knowledge: rank_descending(scorer.score(knowledge)))

@cache
def shuffling_ranker() -> KnowledgeRanker:
    return create_ranker(lambda knowledge: rank_shuffled(knowledge))

@cache
def standard_ranker() -> KnowledgeRanker:
    return overviews_first_ranker()

__all__ = [
    'KnowledgeRanker',
    'create_ranker',
    'lexicographical_ranker',
    'overviews_first_ranker',
    'ascending_ranker',
    'descending_ranker',
    'shuffling_ranker',
    'standard_ranker',
]
