from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset
from llobot.knowledge.indexes import KnowledgeIndex, coerce_index

class KnowledgeRanking:
    _paths: list[Path]
    _hash: int | None

    def __init__(self, paths: Iterable[Path | str] = []):
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

    def __getitem__(self, spec: int | slice) -> Path:
        return self._paths[spec]

    def __iter__(self) -> Iterator[Path]:
        return iter(self._paths)

    def reversed(self) -> KnowledgeRanking:
        return KnowledgeRanking(reversed(self._paths))

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> KnowledgeRanking:
        whitelist = coerce_subset(whitelist)
        return KnowledgeRanking(path for path in self if path in whitelist)

    def __sub__(self, blacklist: KnowledgeSubset | str | KnowledgeIndex | Path) -> KnowledgeRanking:
        return self & ~coerce_subset(blacklist)

def coerce_ranking(what: KnowledgeRanking | Iterable[Path | str]) -> KnowledgeRanking:
    if isinstance(what, KnowledgeRanking):
        return what
    return KnowledgeRanking(what)

def rank_lexicographically(index: KnowledgeIndex | KnowledgeRanking | 'Knowledge') -> KnowledgeRanking:
    index = coerce_index(index)
    return KnowledgeRanking(sorted(index))

def rank_overviews_first(
    index: KnowledgeIndex | KnowledgeRanking | 'Knowledge',
    overviews: KnowledgeSubset | None = None
) -> KnowledgeRanking:
    """
    Creates a knowledge ranking with overview files listed first in each directory.
    The files are otherwise sorted lexicographically.

    Args:
        index: Knowledge index or its precursor to convert to a ranking.
        overviews: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A knowledge ranking with overview files prioritized.
    """
    # Use local import to avoid cycles
    from llobot.knowledge.trees import overviews_first_tree
    tree = overviews_first_tree(index, overviews)
    return tree.ranking

def rank_ascending(scores: 'KnowledgeScores') -> KnowledgeRanking:
    # Sort items with equal score lexicographically.
    paths = rank_lexicographically(scores)
    return KnowledgeRanking(sorted(paths, key=lambda path: scores[path]))

def rank_descending(scores: 'KnowledgeScores') -> KnowledgeRanking:
    return rank_ascending(-scores)

def rank_shuffled(paths: KnowledgeIndex | KnowledgeRanking | 'Knowledge' | 'KnowledgeScores') -> KnowledgeRanking:
    from llobot.knowledge.scores.random import random_scores
    return rank_descending(random_scores(paths))

def rank_in_standard_order(index: KnowledgeIndex | KnowledgeRanking | 'Knowledge') -> KnowledgeRanking:
    return rank_overviews_first(index)

__all__ = [
    'KnowledgeRanking',
    'coerce_ranking',
    'rank_lexicographically',
    'rank_overviews_first',
    'rank_ascending',
    'rank_descending',
    'rank_shuffled',
    'rank_in_standard_order',
]
