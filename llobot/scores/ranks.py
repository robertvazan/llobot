from __future__ import annotations
from itertools import islice
from llobot.scores.decays import DecayScores
import llobot.scores.decays

class RankScores:
    _scores: list[float]

    def __init__(self, scores: Iterable[float | int] = []):
        self._scores = [float(score) for score in scores]

    def __str__(self) -> str:
        return str(self._scores)

    def __len__(self) -> int:
        return len(self._scores)

    def __bool__(self) -> bool:
        return bool(self._scores)

    def __getitem__(self, spec: int | slice) -> float | RankScores:
        if isinstance(spec, slice):
            return RankScores(self._scores[spec])
        return self._scores[spec]

    def __iter__(self) -> Iterator[float]:
        return iter(self._scores)

    def __add__(self, other: RankScores) -> RankScores:
        return RankScores([*self, *other])

    def __mul__(self, other: float | int) -> RankScores:
        return RankScores((score * other for score in self))

    def __rmul__(self, other: float | int) -> RankScores:
        return self * other

def decay(count: int, scores: DecayScores = llobot.scores.decays.standard()) -> RankScores:
    return RankScores(islice(scores, count))

def constant(count: int, value: float | int = 1) -> RankScores:
    return decay(count, llobot.scores.decays.constant(value))

def uniform(count: int, budget: float | int = 1) -> RankScores:
    return constant(count, budget / count)

def zipf(count: int) -> RankScores:
    return decay(count, llobot.scores.decays.zipf())

def exponential(count: int, factor: float = 0.5) -> RankScores:
    return decay(count, llobot.scores.decays.exponential(factor))

def scale_first(factor: float, scores: RankScores) -> RankScores:
    return RankScores(factor * scores[:1] + scores[1:])

def scale_last(factor: float, scores: RankScores) -> RankScores:
    return RankScores(scores[:-1] + factor * scores[-1:])

__all__ = [
    'RankScores',
    'decay',
    'constant',
    'uniform',
    'zipf',
    'exponential',
    'scale_first',
    'scale_last',
]

