from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
import llobot.knowledge.subsets
import llobot.knowledge.indexes

class KnowledgeRanking:
    _paths: list[Path]
    _hash: int | None

    def __init__(self, paths: Iterable[Path | str] = []):
        self._paths = [Path(path) for path in paths]
        self._hash = None

    def __str__(self) -> str:
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
        return KnowledgeRanking(filter(llobot.knowledge.subsets.coerce(whitelist), self))

    def __sub__(self, blacklist: KnowledgeSubset | str | KnowledgeIndex | Path) -> KnowledgeRanking:
        return self & ~llobot.knowledge.subsets.coerce(blacklist)

def coerce(what: KnowledgeRanking | Iterable[Path | str]) -> KnowledgeRanking:
    if isinstance(what, KnowledgeRanking):
        return what
    return KnowledgeRanking(what)

def lexicographical(index: KnowledgeIndex | KnowledgeRanking | 'Knowledge') -> KnowledgeRanking:
    index = llobot.knowledge.indexes.coerce(index)
    return KnowledgeRanking(sorted(index))

def overviews_first(
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
    import llobot.knowledge.trees
    tree = llobot.knowledge.trees.overviews_first(index, overviews)
    return tree.ranking

def ascending(scores: 'KnowledgeScores') -> KnowledgeRanking:
    # Sort items with equal score lexicographically.
    paths = lexicographical(scores)
    return KnowledgeRanking(sorted(paths, key=lambda path: scores[path]))

def descending(scores: 'KnowledgeScores') -> KnowledgeRanking:
    return ascending(-scores)

def shuffle(paths: KnowledgeIndex | KnowledgeRanking | 'Knowledge' | 'KnowledgeScores') -> KnowledgeRanking:
    import llobot.knowledge.scores
    return descending(llobot.knowledge.scores.random(paths))

def standard(index: KnowledgeIndex | KnowledgeRanking | 'Knowledge') -> KnowledgeRanking:
    return overviews_first(index)

__all__ = [
    'KnowledgeRanking',
    'coerce',
    'lexicographical',
    'overviews_first',
    'ascending',
    'descending',
    'shuffle',
    'standard',
]
