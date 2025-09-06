from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import (
    KnowledgeSubset,
    coerce_subset,
)

class KnowledgeIndex:
    _paths: set[Path]
    _hash: int | None

    def __init__(self, paths: Iterable[Path | str] = set()):
        self._paths = set(Path(path) for path in paths)
        self._hash = None

    def __str__(self) -> str:
        return str(self.sorted())

    def __len__(self) -> int:
        return len(self._paths)

    def __bool__(self) -> bool:
        return bool(self._paths)

    def __eq__(self, other) -> bool:
        if not isinstance(other, KnowledgeIndex):
            return NotImplemented
        return self._paths == other._paths

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._paths))
        return self._hash

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._paths

    def __iter__(self) -> Iterator[Path]:
        return iter(self._paths)

    def sorted(self) -> 'KnowledgeRanking':
        import llobot.knowledge.rankings
        return llobot.knowledge.rankings.rank_lexicographically(self)

    def reversed(self) -> 'KnowledgeRanking':
        return self.sorted().reversed()

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> KnowledgeIndex:
        whitelist = coerce_subset(whitelist)
        return KnowledgeIndex(path for path in self if path in whitelist)

    def __or__(self, addition: Path | KnowledgeIndex) -> KnowledgeIndex:
        if isinstance(addition, Path):
            return self | KnowledgeIndex([addition])
        if isinstance(addition, KnowledgeIndex):
            return KnowledgeIndex(self._paths | addition._paths)
        raise TypeError

    def __sub__(self, blacklist: KnowledgeSubset | str | KnowledgeIndex | Path) -> KnowledgeIndex:
        return self & ~coerce_subset(blacklist)

    def __rtruediv__(self, prefix: Path | str) -> KnowledgeIndex:
        prefix = Path(prefix)
        return KnowledgeIndex(prefix/path for path in self)

    def __truediv__(self, subtree: Path | str) -> KnowledgeIndex:
        subtree = Path(subtree)
        return KnowledgeIndex(path.relative_to(subtree) for path in self if path.is_relative_to(subtree))

def coerce_index(what: KnowledgeIndex | 'Knowledge' | 'KnowledgeRanking' | 'KnowledgeScores') -> KnowledgeIndex:
    if isinstance(what, KnowledgeIndex):
        return what
    from llobot.knowledge import Knowledge
    if isinstance(what, Knowledge):
        return what.keys()
    from llobot.knowledge.rankings import KnowledgeRanking
    if isinstance(what, KnowledgeRanking):
        return KnowledgeIndex(what)
    from llobot.knowledge.scores import KnowledgeScores
    if isinstance(what, KnowledgeScores):
        return what.keys()
    raise TypeError

__all__ = [
    'KnowledgeIndex',
    'coerce_index',
]
