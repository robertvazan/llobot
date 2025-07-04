from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.scrapers import Scraper
from llobot.scores.knowledge import KnowledgeScores
from llobot.scores.decays import DecayScores
import llobot.knowledge.graphs
import llobot.knowledge.rankings
import llobot.knowledge.subsets
import llobot.scrapers
import llobot.scores.knowledge
import llobot.scores.decays

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
            return function(knowledge, llobot.scores.knowledge.constant(knowledge))
        def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
            return function(knowledge, initial)
    return LambdaKnowledgeRescorer()

def coerce(material: KnowledgeScorer | KnowledgeSubset | str | Path | KnowledgeIndex) -> KnowledgeScorer:
    if isinstance(material, KnowledgeScorer):
        return material
    subset = llobot.knowledge.subsets.coerce(material)
    return create(lambda knowledge: llobot.scores.knowledge.constant(knowledge.keys() & subset))

@cache
def constant(score: float = 1) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.constant(knowledge, score))

@cache
def uniform(budget: float = 1) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.uniform(knowledge, budget))

@cache
def length() -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.length(knowledge))

@cache
def sqrt_length() -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.sqrt_length(knowledge))

@lru_cache
def shuffle(scores: DecayScores = llobot.scores.decays.standard()) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.shuffle(knowledge, scores))

@lru_cache
def hub(scraper: Scraper = llobot.scrapers.standard()) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.hub(llobot.knowledge.graphs.crawl(knowledge, scraper)))

@lru_cache
def pagerank(scraper: Scraper = llobot.scrapers.standard(), **kwargs) -> KnowledgeScorer:
    return rescorer(lambda knowledge, initial: llobot.scores.knowledge.pagerank(llobot.knowledge.graphs.crawl(knowledge, scraper), knowledge.keys(), initial, **kwargs))

@lru_cache
def reverse_pagerank(scraper: Scraper = llobot.scrapers.standard(), **kwargs) -> KnowledgeScorer:
    return create(lambda knowledge: llobot.scores.knowledge.reverse_pagerank(llobot.knowledge.graphs.crawl(knowledge, scraper), knowledge.keys(), **kwargs))

def _relevance(
    condition: KnowledgeSubset,
    match_score: float,
    non_match_score: float,
    blacklist: KnowledgeSubset | None
) -> KnowledgeScorer:
    # Relevancy scorers have to process the whole project, so optimize the process as much as possible.
    condition = llobot.knowledge.subsets.cached(condition)
    if blacklist:
        blacklist = llobot.knowledge.subsets.cached(blacklist)
        return create(lambda knowledge: KnowledgeScores({
            path: (match_score if condition(path, content) else non_match_score)
            for path, content in knowledge if not blacklist(path, content)
        }))
    else:
        return create(lambda knowledge: KnowledgeScores({
            path: (match_score if condition(path, content) else non_match_score)
            for path, content in knowledge
        }))

@lru_cache
def relevant(relevant: KnowledgeSubset, *,
    blacklist: KnowledgeSubset | None = llobot.knowledge.subsets.boilerplate(),
    unimportant_weight: float = 0.1,
) -> KnowledgeScorer:
    return _relevance(relevant, 1.0, unimportant_weight, blacklist)

@lru_cache
def irrelevant(unimportant: KnowledgeSubset = llobot.knowledge.subsets.unimportant(), *,
    blacklist: KnowledgeSubset | None = llobot.knowledge.subsets.boilerplate(),
    unimportant_weight: float = 0.1,
) -> KnowledgeScorer:
    return _relevance(unimportant, unimportant_weight, 1.0, blacklist)

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
    'shuffle',
    'hub',
    'pagerank',
    'reverse_pagerank',
    'relevant',
    'irrelevant',
    'standard',
]

