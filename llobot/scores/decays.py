from __future__ import annotations
from functools import cache
import math

class DecayScores:
    def __iter__(self) -> Iterator[float]:
        raise NotImplementedError

    @staticmethod
    def _coerce_operand(other: DecayScores | float | int) -> DecayScores:
        if isinstance(other, (int, float)):
            return constant(other)
        return other

    def __add__(self, other: DecayScores | float | int | 'HistoryScores' | 'HistoryScorer') -> DecayScores | 'HistoryScores' | 'HistoryScorer':
        from llobot.scores.history import HistoryScores
        from llobot.scorers.history import HistoryScorer
        if isinstance(other, (HistoryScores, HistoryScorer)):
            return other + self
        other = self._coerce_operand(other)
        return create(lambda: (x + y for x, y in zip(self, other)))

    def __radd__(self, other: float | int) -> DecayScores:
        return self + other

    def __neg__(self) -> DecayScores:
        return create(lambda: (-x for x in self))

    def __sub__(self, other: DecayScores | float | int | 'HistoryScores' | 'HistoryScorer') -> DecayScores | 'HistoryScores' | 'HistoryScorer':
        return self + (-other)

    def __rsub__(self, other: float | int) -> DecayScores:
        return self._coerce_operand(other) - self

    def __mul__(self, other: DecayScores | float | int | 'HistoryScores' | 'HistoryScorer') -> DecayScores | 'HistoryScores' | 'HistoryScorer':
        from llobot.scores.history import HistoryScores
        from llobot.scorers.history import HistoryScorer
        if isinstance(other, (HistoryScores, HistoryScorer)):
            return other * self
        other = self._coerce_operand(other)
        return create(lambda: (x * y for x, y in zip(self, other)))

    def __rmul__(self, other: float | int) -> DecayScores:
        return self * other

    def __truediv__(self, other: DecayScores | float | int | 'HistoryScores' | 'HistoryScorer') -> DecayScores | 'HistoryScores' | 'HistoryScorer':
        from llobot.scores.history import HistoryScores
        from llobot.scorers.history import HistoryScorer
        if isinstance(other, (HistoryScores, HistoryScorer)):
            return self * (1 / other)
        other = self._coerce_operand(other)
        return create(lambda: (x / y for x, y in zip(self, other)))

    def __rtruediv__(self, other: float | int) -> DecayScores:
        return self._coerce_operand(other) / self

def create(constructor: Callable[[], Iterable[float]]) -> DecayScores:
    class LambdaDecayScores(DecayScores):
        def __iter__(self) -> Iterator[float]:
            return iter(constructor())
    return LambdaDecayScores()

@cache
def constant(value: float | int = 1) -> DecayScores:
    def generate():
        while True:
            yield float(value)
    return create(lambda: generate())

@cache
def zipf() -> DecayScores:
    def generate():
        n = 1
        while True:
            yield 1 / n
            n += 1
    return create(lambda: generate())

@cache
def exponential(factor: float = 0.5) -> DecayScores:
    def generate():
        value = 1
        while True:
            yield value
            value *= factor
    return create(lambda: generate())


@cache
def standard() -> DecayScores:
    return zipf()

__all__ = [
    'DecayScores',
    'create',
    'wrap',
    'constant',
    'zipf',
    'exponential',
    'standard',
]

