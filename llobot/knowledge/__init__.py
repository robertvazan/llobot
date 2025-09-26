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
graphs/
    `KnowledgeGraph` for relationship graphs between knowledge items and
    `KnowledgeCrawler` for building them.
trees/
    KnowledgeTree for hierarchical directory tree representations
subsets/
    Pattern-based filtering and selection with KnowledgeSubset
deltas/
    Change tracking for knowledge states. See `deltas.documents`,
    `deltas.knowledge`, `deltas.builder`, and `deltas.diffs`.
archives/
    Historical knowledge storage
resolver
    `KnowledgeResolver` for efficient, proximity-based path resolution.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable, Iterator
from llobot.utils.fs import read_document
from llobot.utils.values import ValueTypeMixin

class Knowledge(ValueTypeMixin):
    """
    An immutable collection of documents, indexed by `pathlib.Path`.

    Knowledge objects behave like a read-only dictionary mapping paths to
    their string content. They support various operations for filtering,
    transforming, and combining knowledge bases.
    """
    _documents: dict[Path, str]

    def __init__(self, documents: dict[Path, str] = {}):
        """
        Initializes a new Knowledge object.

        Args:
            documents: A dictionary of paths and their content.
        """
        self._documents = dict(documents)

    def __repr__(self) -> str:
        return str(self.keys())

    def keys(self) -> 'KnowledgeIndex':
        """Returns a `KnowledgeIndex` of all paths in the collection."""
        from llobot.knowledge.indexes import KnowledgeIndex
        return KnowledgeIndex(self._documents.keys())

    def __len__(self) -> int:
        return len(self._documents)

    @property
    def cost(self) -> int:
        """The total number of characters in all documents."""
        return sum(len(content) for content in self._documents.values())

    def __bool__(self) -> bool:
        return bool(self._documents)

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._documents

    def __getitem__(self, path: Path) -> str:
        """
        Gets the content of a document. Returns an empty string if not found.
        """
        return self._documents.get(path, '')

    def __iter__(self) -> Iterator[(Path, str)]:
        return iter(self._documents.items())

    def transform(self, operation: Callable[[Path, str], str]) -> Knowledge:
        """
        Creates a new `Knowledge` object by applying an operation to each document.
        """
        return Knowledge({path: operation(path, content) for path, content in self})

    def __and__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        """
        Filters the knowledge, keeping only documents in the given subset.
        """
        from llobot.knowledge.subsets import coerce_subset
        subset = coerce_subset(subset)
        return Knowledge({path: content for path, content in self if path in subset})

    def __or__(self, addition: Knowledge) -> Knowledge:
        """
        Merges this knowledge with another, overwriting with new content.
        """
        return Knowledge(self._documents | addition._documents)

    def __sub__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | Path | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        """
        Filters the knowledge, removing documents in the given subset.
        """
        from llobot.knowledge.subsets import coerce_subset
        return self & ~coerce_subset(subset)

    def __rtruediv__(self, prefix: Path | str) -> Knowledge:
        """
        Creates a new `Knowledge` with a prefix prepended to all paths.
        """
        prefix = Path(prefix)
        return Knowledge({prefix/path: content for path, content in self})

    def __truediv__(self, subtree: Path | str) -> Knowledge:
        """
        Creates a new `Knowledge` with a prefix stripped from all paths.

        Only paths within the `subtree` are kept.
        """
        subtree = Path(subtree)
        return Knowledge({path.relative_to(subtree): content for path, content in self if path.is_relative_to(subtree)})

__all__ = [
    'Knowledge',
]
