from __future__ import annotations
import math
from functools import lru_cache
from pathlib import Path
from zlib import crc32
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge.graphs import KnowledgeGraph
import llobot.knowledge.indexes
import llobot.knowledge.subsets
import llobot.knowledge.rankings

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
        if isinstance(other, (int, float)):
            return constant(self, other)
        return coerce(other)

    def __add__(self, other: int | float | KnowledgeScores | Knowledge) -> KnowledgeScores:
        other = self._coerce_operand(other)
        return KnowledgeScores({path: self[path] + other[path] for path in self.keys() | other.keys()})

    def __radd__(self, other: int | float) -> KnowledgeScores:
        return self + other

    def __sub__(self, other: int | float | KnowledgeScores | Knowledge | KnowledgeSubset | str | KnowledgeIndex | KnowledgeRanking) -> KnowledgeScores:
        if isinstance(other, (KnowledgeSubset, str, KnowledgeIndex, KnowledgeRanking)):
            return self & ~llobot.knowledge.subsets.coerce(other)
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
        subset = llobot.knowledge.subsets.coerce(subset)
        return KnowledgeScores({path: score for path, score in self if path in subset})

    def __or__(self, other: KnowledgeScores) -> KnowledgeScores:
        return KnowledgeScores(self._scores | other._scores)

    def transform(self, function: Callable[[float], float]) -> KnowledgeScores:
        return KnowledgeScores({path: function(score) for path, score in self})

    def total(self) -> float:
        return sum(self._scores.values())

    def highest(self) -> float | None:
        return max(self._scores.values(), default=None)

    def clip_below(self, threshold: float | int) -> KnowledgeScores:
        return KnowledgeScores({path: score for path, score in self if score >= threshold})

def coerce(what: KnowledgeScores | Knowledge | KnowledgeIndex | KnowledgeRanking) -> KnowledgeScores:
    if isinstance(what, KnowledgeScores):
        return what
    if isinstance(what, Knowledge):
        return length(what)
    if isinstance(what, (KnowledgeIndex, KnowledgeRanking)):
        return constant(what)
    raise TypeError(what)

def normalize(denormalized: KnowledgeScores, budget: float = 1) -> KnowledgeScores:
    total = denormalized.total()
    if not total:
        return denormalized
    return (budget / total) * denormalized

def constant(keys: KnowledgeIndex | KnowledgeRanking | Knowledge | KnowledgeScores, score: float = 1) -> KnowledgeScores:
    keys = llobot.knowledge.indexes.coerce(keys)
    return KnowledgeScores({path: score for path in keys})

def uniform(keys: KnowledgeIndex | KnowledgeRanking | Knowledge | KnowledgeScores, budget: float = 1) -> KnowledgeScores:
    keys = llobot.knowledge.indexes.coerce(keys)
    return constant(keys, budget / len(keys)) if keys else KnowledgeScores()

def length(knowledge: Knowledge) -> KnowledgeScores:
    return KnowledgeScores({path: len(content) for path, content in knowledge})

def sqrt_length(knowledge: Knowledge) -> KnowledgeScores:
    return KnowledgeScores({path: math.sqrt(len(content)) for path, content in knowledge})

# This uses only path, not content, so that content changes do not cause cache-killing reorderings.
def random(paths: KnowledgeIndex | KnowledgeRanking | Knowledge | KnowledgeScores) -> KnowledgeScores:
    paths = llobot.knowledge.indexes.coerce(paths)
    # Here we have to be careful to avoid zero scores, so that the resulting score object has all the paths.
    return KnowledgeScores({path: crc32(str(path).encode('utf-8')) or 1 for path in paths})

def hub(graph: KnowledgeGraph) -> KnowledgeScores:
    return KnowledgeScores({path: len(targets) for path, targets in graph.symmetrical()})

@lru_cache(maxsize=2)
def pagerank(
    graph: KnowledgeGraph,
    nodes: KnowledgeIndex = KnowledgeIndex(),
    initial: KnowledgeScores = KnowledgeScores(),
    *,
    damping: float = 0.85,
    iterations: int = 100,
    tolerance: float = 1.0e-3
) -> KnowledgeScores:
    if not graph and not nodes:
        return KnowledgeScores()
    # This implementation is optimized to use Python's built-in types and integer-addressed lists,
    # because the neat version using our high-level classes was too slow.
    backlinks = graph.reverse()
    nodes = nodes | graph.keys() | backlinks.keys()
    ranking = list(llobot.knowledge.rankings.lexicographical(nodes))
    path_ids = {path: i for i, path in enumerate(ranking)}
    count = len(ranking)
    graph_table = [tuple(path_ids[target] for target in graph[source]) for source in ranking]
    backlinks_table = [tuple(path_ids[source] for source in backlinks[target]) for target in ranking]
    sinks = [i for i, targets in enumerate(graph_table) if not targets]
    if initial:
        initial_norm = count / initial.total()
        initial_table = [initial[path] * initial_norm for path in ranking]
    else:
        initial_table = [1.0] * count
    scores = initial_table
    for _ in range(iterations):
        new_scores = [0.0] * count
        sink_spread = sum(scores[source] for source in sinks) / count
        for target in range(count):
            incoming = initial_table[target] * sink_spread
            for source in backlinks_table[target]:
                targets = graph_table[source]
                if targets:
                    incoming += scores[source] / len(targets)
            new_scores[target] = (1 - damping) * initial_table[target] + damping * incoming
        delta = sum(abs(new_scores[i] - scores[i]) for i in range(count)) / count
        scores = new_scores
        if delta < tolerance:
            break
    return KnowledgeScores({ranking[i]: scores[i] for i in range(count)})

def reverse_pagerank(graph: KnowledgeGraph, nodes: KnowledgeIndex = KnowledgeIndex(), **kwargs) -> KnowledgeScores:
    return pagerank(graph.reverse(), nodes, **kwargs)

def prioritize(
    index: Knowledge | KnowledgeIndex | KnowledgeRanking | KnowledgeScores,
    subset: KnowledgeSubset | str | Path | KnowledgeIndex,
    *,
    background_score: float = 0.001
) -> KnowledgeScores:
    """
    Assigns a high score to documents in a subset and a low background score to other documents.
    """
    index = llobot.knowledge.indexes.coerce(index)
    subset = llobot.knowledge.subsets.coerce(subset)
    priority_scores = coerce(index & subset)
    background_scores = uniform(index, background_score)
    return background_scores + priority_scores

__all__ = [
    'KnowledgeScores',
    'coerce',
    'normalize',
    'constant',
    'uniform',
    'length',
    'sqrt_length',
    'random',
    'hub',
    'pagerank',
    'reverse_pagerank',
    'prioritize',
]
