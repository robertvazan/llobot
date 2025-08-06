from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.scrapers import GraphScraper
from llobot.knowledge.scores import KnowledgeScores
import llobot.knowledge.subsets
import llobot.scrapers
import llobot.knowledge.scores

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
            return constant(self, other)
        return other

    def __add__(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        other = self._coerce_operand(other)
        return create(lambda knowledge: self(knowledge) + other(knowledge))

    def __radd__(self, other: int | float) -> KnowledgeScorer:
        return self + other

    def __sub__(self, other: KnowledgeScorer | int | float | KnowledgeSubset | str) -> KnowledgeScorer:
        if isinstance(other, (KnowledgeSubset, str)):
            other = llobot.knowledge.subsets.coerce(other)
            return self & ~other
        other = self._coerce_operand(other)
        return create(lambda knowledge: self(knowledge) - other(knowledge))

    def __rsub__(self, other: int | float) -> KnowledgeScorer:
        return self._coerce_operand(other) - self

    def __neg__(self) -> KnowledgeScorer:
        return 0 - self

    def __mul__(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        if isinstance(other, (KnowledgeSubset, str)):
            return self & ~llobot.knowledge.subsets.coerce(other)
        other = self._coerce_operand(other)
        return create(lambda knowledge: self(knowledge) * other(knowledge))

    def __rmul__(self, other: int | float) -> KnowledgeScorer:
        return self * other

    def __truediv__(self, other: KnowledgeScorer | int | float) -> KnowledgeScorer:
        other = self._coerce_operand(other)
        return create(lambda knowledge: self(knowledge) / other(knowledge))

    def __rtruediv__(self, other: int | float) -> KnowledgeScorer:
        return self._coerce_operand(other) / self

    def __and__(self, subset: KnowledgeSubset | str) -> KnowledgeScorer:
        subset = llobot.knowledge.subsets.coerce(subset)
        # Here we have to be careful to filter by subset before the underlying scorer is invoked,
        # so that uniform scorer spreads its budget only over documents in the subset.
        return create(lambda knowledge: self(knowledge & subset))

    def __or__(self, other: KnowledgeScorer) -> KnowledgeScorer:
        return create(lambda knowledge: self(knowledge) | other(knowledge))

def create(function: Callable[[Knowledge], KnowledgeScores]) -> KnowledgeScorer:
    class LambdaKnowledgeScorer(KnowledgeScorer):
        def score(self, knowledge: Knowledge) -> KnowledgeScores:
            return function(knowledge)
    return LambdaKnowledgeScorer()

def rescorer(function: Callable[[Knowledge, KnowledgeScores], KnowledgeScores]) -> KnowledgeScorer:
    class LambdaKnowledgeRescorer(KnowledgeScorer):
        def score(self, knowledge: Knowledge) -> KnowledgeScores:
            return function(knowledge, llobot.knowledge.scores.constant(knowledge))
        def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
            return function(knowledge, initial)
    return LambdaKnowledgeRescorer()

def coerce(material: KnowledgeScorer | KnowledgeSubset | str | Path | KnowledgeIndex) -> KnowledgeScorer:
    if isinstance(material, KnowledgeScorer):
        return material
    subset = llobot.knowledge.subsets.coerce(material)
    return create(lambda knowledge: llobot.knowledge.scores.constant(knowledge.keys() & subset))

@cache
def constant(score: float = 1) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.knowledge.scores.constant(knowledge, score))

@cache
def uniform(budget: float = 1) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.knowledge.scores.uniform(knowledge, budget))

@cache
def length() -> KnowledgeScorer:
    return create(lambda knowledge: llobot.knowledge.scores.length(knowledge))

@cache
def sqrt_length() -> KnowledgeScorer:
    return create(lambda knowledge: llobot.knowledge.scores.sqrt_length(knowledge))

@lru_cache
def hub(scraper: GraphScraper = llobot.scrapers.standard()) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.knowledge.scores.hub(scraper(knowledge)))

@lru_cache
def pagerank(scraper: GraphScraper = llobot.scrapers.standard(), **kwargs) -> KnowledgeScorer:
    return rescorer(lambda knowledge, initial: llobot.knowledge.scores.pagerank(scraper(knowledge), knowledge.keys(), initial, **kwargs))

@lru_cache
def reverse_pagerank(scraper: GraphScraper = llobot.scrapers.standard(), **kwargs) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.knowledge.scores.reverse_pagerank(scraper(knowledge), knowledge.keys(), **kwargs))

def _relevance(
    condition: KnowledgeSubset,
    match_score: float,
    non_match_score: float,
    blacklist: KnowledgeSubset | None
) -> KnowledgeScorer:
    if blacklist:
        return create(lambda knowledge: KnowledgeScores({
            path: (match_score if path in condition else non_match_score)
            for path in knowledge.keys() if path not in blacklist
        }))
    else:
        return create(lambda knowledge: KnowledgeScores({
            path: (match_score if path in condition else non_match_score)
            for path in knowledge.keys()
        }))

# Positive relevance scorer.
@lru_cache
def relevant(relevant: KnowledgeSubset, *,
    blacklist: KnowledgeSubset | None = llobot.knowledge.subsets.boilerplate(),
    ancillary_weight: float = 0.1,
) -> KnowledgeScorer:
    return _relevance(relevant, 1.0, ancillary_weight, blacklist)

# Negative relevance scorer.
@lru_cache
def irrelevant(ancillary: KnowledgeSubset = llobot.knowledge.subsets.ancillary(), *,
    blacklist: KnowledgeSubset | None = llobot.knowledge.subsets.boilerplate(),
    ancillary_weight: float = 0.1,
) -> KnowledgeScorer:
    return _relevance(ancillary, ancillary_weight, 1.0, blacklist)

@cache
def standard() -> KnowledgeScorer:
    return pagerank()

__all__ = [
    'KnowledgeScorer',
    'create',
    'coerce',
    'constant',
    'uniform',
    'length',
    'sqrt_length',
    'hub',
    'pagerank',
    'reverse_pagerank',
    'relevant',
    'irrelevant',
    'standard',
]
