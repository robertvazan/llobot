"""
Data structures and functions for ordering knowledge documents.

This package defines `KnowledgeRanking`, an ordered list of document paths,
and `KnowledgeRanker`, a strategy for creating rankings from a `Knowledge` base.

Submodules
----------
rankers
    Base `KnowledgeRanker` and standard ranker implementations.
lexicographical
    Rankers that sort documents lexicographically.
sorting
    Rankers that sort documents based on scores.
overviews
    Rankers that prioritize overview documents.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset

class KnowledgeRanking:
    """
    Represents an immutable, ordered sequence of document paths.
    """
    _paths: list[Path]
    _hash: int | None

    def __init__(self, paths: Iterable[Path | str] = []):
        """
        Initializes a new KnowledgeRanking.

        Args:
            paths: An iterable of paths or path strings.
        """
        self._paths = [Path(path) for path in paths]
        self._hash = None

    def __repr__(self) -> str:
        return str(self._paths)

    def __len__(self) -> int:
        return len(self._paths)

    def __bool__(self) -> bool:
        return bool(self._paths)

    def __eq__(self, other) -> bool:
        if not isinstance(other, KnowledgeRanking):
            return NotImplemented
        return self._paths == other._paths

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(tuple(self._paths))
        return self._hash

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._paths

    def __getitem__(self, spec: int | slice) -> Path | KnowledgeRanking:
        if isinstance(spec, slice):
            return KnowledgeRanking(self._paths[spec])
        return self._paths[spec]

    def __iter__(self) -> Iterator[Path]:
        return iter(self._paths)

    def reversed(self) -> KnowledgeRanking:
        """
        Returns a new ranking with the paths in reverse order.
        """
        return KnowledgeRanking(reversed(self._paths))

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> KnowledgeRanking:
        """
        Filters the ranking, keeping only paths in the given whitelist.
        """
        whitelist = coerce_subset(whitelist)
        return KnowledgeRanking(path for path in self if path in whitelist)

    def __sub__(self, blacklist: KnowledgeSubset | str | KnowledgeIndex | Path) -> KnowledgeRanking:
        """
        Filters the ranking, removing paths in the given blacklist.
        """
        return self & ~coerce_subset(blacklist)

type KnowledgeRankingPrecursor = KnowledgeRanking | KnowledgeIndex | Knowledge

def coerce_ranking(what: KnowledgeRankingPrecursor | Iterable[Path | str]) -> KnowledgeRanking:
    """
    Coerces various objects into a `KnowledgeRanking`.

    - `KnowledgeRanking` is returned as is.
    - `KnowledgeIndex` and `Knowledge` are converted to a lexicographically
      sorted ranking.
    - An iterable of paths is converted to a `KnowledgeRanking`.
    """
    if isinstance(what, KnowledgeRanking):
        return what
    # Local import to avoid cycles.
    from llobot.knowledge import Knowledge
    from llobot.knowledge.indexes import KnowledgeIndex
    from llobot.knowledge.ranking.lexicographical import rank_lexicographically
    if isinstance(what, (KnowledgeIndex, Knowledge)):
        return rank_lexicographically(what)
    return KnowledgeRanking(what)

def standard_ranking(index: KnowledgeRankingPrecursor) -> KnowledgeRanking:
    """
    Creates a knowledge ranking in the standard order.

    The standard order is lexicographical, but with overview files prioritized
    to appear before their siblings in the directory tree.
    """
    # Local import to avoid cycles.
    from llobot.knowledge.ranking.lexicographical import rank_lexicographically
    from llobot.knowledge.ranking.overviews import rank_overviews_before_siblings
    return rank_overviews_before_siblings(rank_lexicographically(index))

__all__ = [
    'KnowledgeRanking',
    'KnowledgeRankingPrecursor',
    'coerce_ranking',
    'standard_ranking',
]
