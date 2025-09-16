"""
Knowledge management system for llobot.

This module provides the core Knowledge class and directory loading functionality.
Knowledge represents a collection of documents indexed by Path, supporting various
operations like filtering, transformation, and combination with other knowledge sets.

Submodules and Subpackages
---------------------------

indexes
    KnowledgeIndex for path-based indexing and set operations
ranking
    KnowledgeRanking for ordered sequences of knowledge paths
scores/
    Provides `KnowledgeScores` for representing document scores and `KnowledgeScorer`
    for implementing scoring strategies. Includes various scorer implementations
    like PageRank, length-based, and relevance-based scoring, as well as
    functions for score aggregation and normalization.
graphs
    KnowledgeGraph for relationship graphs between knowledge items
trees
    KnowledgeTree for hierarchical directory tree representations
subsets/
    Pattern-based filtering and selection with KnowledgeSubset
deltas/
    Change tracking for knowledge states. See `deltas.documents`,
    `deltas.knowledge`, `deltas.builder`, and `deltas.diffs`.
archives/
    Historical knowledge storage
"""
from __future__ import annotations
from pathlib import Path
from llobot.utils.fs import read_document

class Knowledge:
    _documents: dict[Path, str]
    _hash: int | None

    def __init__(self, documents: dict[Path, str] = {}):
        self._documents = dict(documents)
        self._hash = None

    def __repr__(self) -> str:
        return str(self.keys())

    def keys(self) -> 'KnowledgeIndex':
        from llobot.knowledge.indexes import KnowledgeIndex
        return KnowledgeIndex(self._documents.keys())

    def __len__(self) -> int:
        return len(self._documents)

    @property
    def cost(self) -> int:
        return sum(len(content) for content in self._documents.values())

    def __bool__(self) -> bool:
        return bool(self._documents)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Knowledge):
            return NotImplemented
        return self._documents == other._documents

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._documents.items()))
        return self._hash

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._documents

    def __getitem__(self, path: Path) -> str:
        return self._documents.get(path, '')

    def __iter__(self) -> Iterator[(Path, str)]:
        return iter(self._documents.items())

    def transform(self, operation: Callable[[Path, str], str]) -> Knowledge:
        return Knowledge({path: operation(path, content) for path, content in self})

    def __and__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        from llobot.knowledge.subsets import coerce_subset
        subset = coerce_subset(subset)
        return Knowledge({path: content for path, content in self if path in subset})

    def __or__(self, addition: Knowledge) -> Knowledge:
        return Knowledge(self._documents | addition._documents)

    def __sub__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | Path | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        from llobot.knowledge.subsets import coerce_subset
        return self & ~coerce_subset(subset)

    def __rtruediv__(self, prefix: Path | str) -> Knowledge:
        prefix = Path(prefix)
        return Knowledge({prefix/path: content for path, content in self})

    def __truediv__(self, subtree: Path | str) -> Knowledge:
        subtree = Path(subtree)
        return Knowledge({path.relative_to(subtree): content for path, content in self if path.is_relative_to(subtree)})

__all__ = [
    'Knowledge',
]
