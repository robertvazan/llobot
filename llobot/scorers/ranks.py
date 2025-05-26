from __future__ import annotations
from functools import cache, lru_cache
from llobot.scores.decays import DecayScores
from llobot.scores.ranks import RankScores
import llobot.scores.decays
import llobot.scores.ranks

class RankScorer:
    def score(self, count: int) -> RankScores:
        raise NotImplementedError

    def __call__(self, count: int) -> RankScores:
        return self.score(count)

def create(function: Callable[[int], RankScores]) -> RankScorer:
    class LambdaRankScorer(RankScorer):
        def score(self, count: int) -> RankScores:
            return function(count)
    return LambdaRankScorer()

@lru_cache
def decay(scores: DecayScores = llobot.scores.decays.standard()) -> RankScorer:
    return create(lambda count: llobot.scores.ranks.decay(count, scores))

@cache
def constant(value: float = 1) -> RankScorer:
    return create(lambda count: llobot.scores.ranks.constant(count, value))

@cache
def uniform(budget: float = 1) -> RankScorer:
    return create(lambda count: llobot.scores.ranks.uniform(count, budget))

@cache
def zipf() -> RankScorer:
    return create(lambda count: llobot.scores.ranks.zipf(count))

@cache
def exponential(factor: float = 0.5) -> RankScorer:
    return create(lambda count: llobot.scores.ranks.exponential(count, factor))

def scale_first(factor: float, scorer: RankScorer) -> RankScorer:
    return create(lambda count: llobot.scores.ranks.scale_first(factor, scorer(count)))

def scale_last(factor: float, scorer: RankScorer) -> RankScorer:
    return create(lambda count: llobot.scores.ranks.scale_last(factor, scorer(count)))

@cache
def fast() -> RankScorer:
    return exponential()

@cache
def slow() -> RankScorer:
    return zipf()

@cache
def fast_with_fallback() -> RankScorer:
    return scale_last(0.001, fast())

@cache
def slow_with_fallback() -> RankScorer:
    return scale_last(0.001, slow())

__all__ = [
    'RankScorer',
    'create',
    'decay',
    'constant',
    'uniform',
    'zipf',
    'exponential',
    'scale_first',
    'scale_last',
    'fast',
    'slow',
    'fast_with_fallback',
    'slow_with_fallback',
]

