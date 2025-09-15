"""
Data structures and functions for scoring knowledge documents.

This package defines `KnowledgeScores`, a mapping from document paths to numerical
scores, and `KnowledgeScorer`, a strategy for assigning scores to documents in a
`Knowledge` base.

Submodules
----------
scorers
    Base `KnowledgeScorer` and standard scorer implementations.
constant
    Scorers that assign a constant score.
uniform
    Scorers that distribute a total score budget uniformly.
length
    Scorers based on document length.
random
    Scorers that assign random scores for shuffling.
directory
    Functions to aggregate scores by directory.
pagerank
    Scorers based on the PageRank algorithm over the knowledge graph.
relevance
    Scorers that assign scores based on relevance to a subset.
subset
    Scorer for an explicit subset of documents.
normal
    Functions for score normalization.
"""
from __future__ import annotations
import math
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset
from llobot.knowledge.indexes import KnowledgeIndex, coerce_index
from llobot.knowledge.rankings import KnowledgeRanking

class KnowledgeScores:
    _scores: dict[Path, float]
    _hash: int | None

    def __init__(self, scores: dict[Path, float] = {}):
        self._scores = {path: float(score) for path, score in scores.items() if math.isfinite(score) and score != 0}
        self._hash = None

    def __str__(self) -> str:
        return str(self._scores)

    def keys(self) -> KnowledgeIndex:
        return KnowledgeIndex(self._scores.keys())

    def __len__(self) -> int:
        return len(self._scores)

    def __bool__(self) -> bool:
        return bool(self._scores)

    def __eq__(self, other) -> bool:
        if not isinstance(other, KnowledgeScores):
            return NotImplemented
        return self._scores == other._scores

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._scores.items()))
        return self._hash

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._scores

    def __getitem__(self, path: Path) -> float:
        return self._scores.get(path, 0)

    def __iter__(self) -> Iterator[(Path, float)]:
        return iter(self._scores.items())

    def _coerce_operand(self, other: int | float | KnowledgeScores | Knowledge) -> KnowledgeScores:
        from llobot.knowledge.scores.constant import constant_scores
        if isinstance(other, (int, float)):
            return constant_scores(self, other)
        return coerce_scores(other)

    def __add__(self, other: int | float | KnowledgeScores | Knowledge) -> KnowledgeScores:
        other = self._coerce_operand(other)
        return KnowledgeScores({path: self[path] + other[path] for path in self.keys() | other.keys()})

    def __radd__(self, other: int | float) -> KnowledgeScores:
        return self + other

    def __sub__(self, other: int | float | KnowledgeScores | Knowledge | KnowledgeSubset | str | KnowledgeIndex | KnowledgeRanking) -> KnowledgeScores:
        if isinstance(other, (KnowledgeSubset, str, KnowledgeIndex, KnowledgeRanking)):
            return self & ~coerce_subset(other)
        other = self._coerce_operand(other)
        return KnowledgeScores({path: self[path] - other[path] for path in self.keys() | other.keys()})

    def __rsub__(self, other: int | float) -> KnowledgeScores:
        return self._coerce_operand(other) - self

    def __neg__(self) -> KnowledgeScores:
        return 0 - self

    def __mul__(self, other: int | float | KnowledgeScores | Knowledge) -> KnowledgeScores:
        other = self._coerce_operand(other)
        return KnowledgeScores({path: self[path] * other[path] for path in self.keys() & other.keys()})

    def __rmul__(self, other: int | float) -> KnowledgeScores:
        return self * other

    def __truediv__(self, other: int | float | KnowledgeScores | Knowledge) -> KnowledgeScores:
        other = self._coerce_operand(other)
        return KnowledgeScores({path: self[path] / other[path] for path in self.keys() & other.keys()})

    def __rtruediv__(self, other: int | float) -> KnowledgeScores:
        return self._coerce_operand(other) / self

    def __and__(self, subset: KnowledgeSubset | str | KnowledgeIndex | KnowledgeRanking | Knowledge) -> KnowledgeScores:
        subset = coerce_subset(subset)
        return KnowledgeScores({path: score for path, score in self if path in subset})

    def __or__(self, other: KnowledgeScores) -> KnowledgeScores:
        return KnowledgeScores(self._scores | other._scores)

    def total(self) -> float:
        return sum(self._scores.values())

def coerce_scores(what: KnowledgeScores | Knowledge | KnowledgeIndex | KnowledgeRanking) -> KnowledgeScores:
    from llobot.knowledge.scores.constant import constant_scores
    from llobot.knowledge.scores.length import score_length
    if isinstance(what, KnowledgeScores):
        return what
    if isinstance(what, Knowledge):
        return score_length(what)
    if isinstance(what, (KnowledgeIndex, KnowledgeRanking)):
        return constant_scores(what)
    raise TypeError(what)

__all__ = [
    'KnowledgeScores',
    'coerce_scores',
]
