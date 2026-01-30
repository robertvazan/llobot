"""
Knowledge management system for llobot.

This module provides the core Knowledge class and directory loading functionality.
Knowledge represents a collection of documents indexed by PurePosixPath, supporting
various operations like filtering, transformation, and combination with other knowledge
sets.

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
resolver
    `KnowledgeResolver` for efficient, proximity-based path resolution.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Callable, Iterator
from llobot.utils.fs import read_document
from llobot.utils.values import ValueTypeMixin
from llobot.formats.paths import coerce_path

if TYPE_CHECKING:
    from llobot.knowledge.indexes import KnowledgeIndex
    from llobot.knowledge.ranking import KnowledgeRanking
    from llobot.knowledge.scores import KnowledgeScores
    from llobot.knowledge.subsets import KnowledgeSubset

class Knowledge(ValueTypeMixin):
    """
    An immutable collection of documents, indexed by `pathlib.PurePosixPath`.

    Knowledge objects behave like a read-only dictionary mapping paths to
    their string content. They support various operations for filtering,
    transforming, and combining knowledge bases.
    """
    _documents: dict[PurePosixPath, str]

    def __init__(self, documents: dict[PurePosixPath, str] | None = None):
        """
        Initializes a new Knowledge object.

        Args:
            documents: A dictionary of paths and their content.
        """
        if documents is None:
            documents = {}
        self._documents = {coerce_path(p): c for p, c in documents.items()}

    def __repr__(self) -> str:
        return str(self.keys())

    def keys(self) -> KnowledgeIndex:
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

    def __contains__(self, path: PurePosixPath | str) -> bool:
        return PurePosixPath(path) in self._documents

    def __getitem__(self, path: PurePosixPath) -> str:
        """
        Gets the content of a document. Returns an empty string if not found.
        """
        return self._documents.get(path, '')

    def __iter__(self) -> Iterator[tuple[PurePosixPath, str]]:
        return iter(self._documents.items())

    def transform(self, operation: Callable[[PurePosixPath, str], str]) -> Knowledge:
        """
        Creates a new `Knowledge` object by applying an operation to each document.
        """
        return Knowledge({path: operation(path, content) for path, content in self})

    def __and__(self, subset: KnowledgeSubset | str | PurePosixPath | KnowledgeIndex | KnowledgeRanking | KnowledgeScores) -> Knowledge:
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

    def __sub__(self, subset: KnowledgeSubset | str | PurePosixPath | KnowledgeIndex | PurePosixPath | KnowledgeRanking | KnowledgeScores) -> Knowledge:
        """
        Filters the knowledge, removing documents in the given subset.
        """
        from llobot.knowledge.subsets import coerce_subset
        return self & ~coerce_subset(subset)

    def __rtruediv__(self, prefix: PurePosixPath | str) -> Knowledge:
        """
        Creates a new `Knowledge` with a prefix prepended to all paths.
        """
        prefix = PurePosixPath(prefix)
        return Knowledge({prefix/path: content for path, content in self})

    def __truediv__(self, subtree: PurePosixPath | str) -> Knowledge:
        """
        Creates a new `Knowledge` with a prefix stripped from all paths.

        Only paths within the `subtree` are kept.
        """
        subtree = PurePosixPath(subtree)
        return Knowledge({path.relative_to(subtree): content for path, content in self if path.is_relative_to(subtree)})

__all__ = [
    'Knowledge',
]
