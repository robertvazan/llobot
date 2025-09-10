from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset
from llobot.knowledge.subsets.standard import boilerplate_subset, ancillary_subset
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.scrapers import GraphScraper, standard_scraper
from llobot.knowledge.scores import (
    KnowledgeScores,
    constant_scores,
    uniform_scores,
    score_length,
    score_sqrt_length,
    hub_scores,
    pagerank_scores,
    reverse_pagerank_scores,
)

# Returned scores represent relative worth of every document.
# Relationship between score and document worth should be linear, so that document with double value has double score.
# What is considered to be the worth of a document is however up to the scorer.
# Scorers are also free to scale scores however they want.
class KnowledgeScorer:
    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        return KnowledgeScores()

    def __call__(self, knowledge: Knowledge) -> KnowledgeScores:
        return self.score(knowledge)

    # Some scorers (PageRank) can reflow scores from arbitrary initial state.
    def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
        # Multiplication is the default way to chain scorers.
        return initial * self(knowledge)

    def _coerce_operand(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        if isinstance(other, (int, float)):
            return constant_scorer(self, other)
        return other

    def __add__(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        other = self._coerce_operand(other)
        return create_scorer(lambda knowledge: self(knowledge) + other(knowledge))

    def __radd__(self, other: int | float) -> KnowledgeScorer:
        return self + other

    def __sub__(self, other: KnowledgeScorer | int | float | KnowledgeSubset | str) -> KnowledgeScorer:
        if isinstance(other, (KnowledgeSubset, str)):
            return self & ~coerce_subset(other)
        other = self._coerce_operand(other)
        return create_scorer(lambda knowledge: self(knowledge) - other(knowledge))

    def __rsub__(self, other: int | float) -> KnowledgeScorer:
        return self._coerce_operand(other) - self

    def __neg__(self) -> KnowledgeScorer:
        return 0 - self

    def __mul__(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        if isinstance(other, (KnowledgeSubset, str)):
            return self & ~coerce_subset(other)
        other = self._coerce_operand(other)
        return create_scorer(lambda knowledge: self(knowledge) * other(knowledge))

    def __rmul__(self, other: int | float) -> KnowledgeScorer:
        return self * other

    def __truediv__(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        other = self._coerce_operand(other)
        return create_scorer(lambda knowledge: self(knowledge) / other(knowledge))

    def __rtruediv__(self, other: int | float) -> KnowledgeScorer:
        return self._coerce_operand(other) / self

    def __and__(self, subset: KnowledgeSubset | str) -> KnowledgeScorer:
        subset = coerce_subset(subset)
        # Here we have to be careful to filter by subset before the underlying scorer is invoked,
        # so that uniform scorer spreads its budget only over documents in the subset.
        return create_scorer(lambda knowledge: self(knowledge & subset))

    def __or__(self, other: KnowledgeScorer) -> KnowledgeScorer:
        return create_scorer(lambda knowledge: self(knowledge) | other(knowledge))

def create_scorer(function: Callable[[Knowledge], KnowledgeScores]) -> KnowledgeScorer:
    class LambdaKnowledgeScorer(KnowledgeScorer):
        def score(self, knowledge: Knowledge) -> KnowledgeScores:
            return function(knowledge)
    return LambdaKnowledgeScorer()

def create_rescorer(function: Callable[[Knowledge, KnowledgeScores], KnowledgeScores]) -> KnowledgeScorer:
    class LambdaKnowledgeRescorer(KnowledgeScorer):
        def score(self, knowledge: Knowledge) -> KnowledgeScores:
            return function(knowledge, constant_scores(knowledge))
        def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
            return function(knowledge, initial)
    return LambdaKnowledgeRescorer()

def coerce_scorer(material: KnowledgeScorer | KnowledgeSubset | str | Path | KnowledgeIndex) -> KnowledgeScorer:
    if isinstance(material, KnowledgeScorer):
        return material
    subset = coerce_subset(material)
    return create_scorer(lambda knowledge: constant_scores(knowledge.keys() & subset))

@cache
def constant_scorer(score: float = 1) -> KnowledgeScorer:
    return create_scorer(lambda knowledge: constant_scores(knowledge, score))

@cache
def uniform_scorer(budget: float = 1) -> KnowledgeScorer:
    return create_scorer(lambda knowledge: uniform_scores(knowledge, budget))

@cache
def length_scorer() -> KnowledgeScorer:
    return create_scorer(lambda knowledge: score_length(knowledge))

@cache
def sqrt_length_scorer() -> KnowledgeScorer:
    return create_scorer(lambda knowledge: score_sqrt_length(knowledge))

@lru_cache
def hub_scorer(scraper: GraphScraper = standard_scraper()) -> KnowledgeScorer:
    return create_scorer(lambda knowledge: hub_scores(scraper(knowledge)))

@lru_cache
def pagerank_scorer(scraper: GraphScraper = standard_scraper(), **kwargs) -> KnowledgeScorer:
    return create_rescorer(lambda knowledge, initial: pagerank_scores(scraper(knowledge), knowledge.keys(), initial, **kwargs))

@lru_cache
def reverse_pagerank_scorer(scraper: GraphScraper = standard_scraper(), **kwargs) -> KnowledgeScorer:
    return create_scorer(lambda knowledge: reverse_pagerank_scores(scraper(knowledge), knowledge.keys(), **kwargs))

def _relevance(
    condition: KnowledgeSubset,
    match_score: float,
    non_match_score: float,
    blacklist: KnowledgeSubset | None
) -> KnowledgeScorer:
    if blacklist:
        return create_scorer(lambda knowledge: KnowledgeScores({
            path: (match_score if path in condition else non_match_score)
            for path in knowledge.keys() if path not in blacklist
        }))
    else:
        return create_scorer(lambda knowledge: KnowledgeScores({
            path: (match_score if path in condition else non_match_score)
            for path in knowledge.keys()
        }))

# Positive relevance scorer.
@lru_cache
def relevant_subset_scorer(relevant: KnowledgeSubset, *,
    blacklist: KnowledgeSubset | None = boilerplate_subset(),
    ancillary_weight: float = 0.1,
) -> KnowledgeScorer:
    return _relevance(relevant, 1.0, ancillary_weight, blacklist)

# Negative relevance scorer.
@lru_cache
def irrelevant_subset_scorer(ancillary: KnowledgeSubset = ancillary_subset(), *,
    blacklist: KnowledgeSubset | None = boilerplate_subset(),
    ancillary_weight: float = 0.1,
) -> KnowledgeScorer:
    return _relevance(ancillary, ancillary_weight, 1.0, blacklist)

@cache
def standard_scorer() -> KnowledgeScorer:
    return pagerank_scorer()

__all__ = [
    'KnowledgeScorer',
    'create_scorer',
    'create_rescorer',
    'coerce_scorer',
    'constant_scorer',
    'uniform_scorer',
    'length_scorer',
    'sqrt_length_scorer',
    'hub_scorer',
    'pagerank_scorer',
    'reverse_pagerank_scorer',
    'relevant_subset_scorer',
    'irrelevant_subset_scorer',
    'standard_scorer',
]
