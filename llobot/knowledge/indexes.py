from __future__ import annotations
from pathlib import PurePosixPath
from typing import Iterable, Iterator
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset

class KnowledgeIndex(ValueTypeMixin):
    """
    An immutable, unordered collection of unique `pathlib.PurePosixPath` objects.

    This class behaves like a read-only set of paths, providing set operations
    and path manipulation methods.
    """
    _paths: frozenset[PurePosixPath]

    def __init__(self, paths: Iterable[PurePosixPath | str] = set()):
        """
        Initializes a new `KnowledgeIndex`.

        Args:
            paths: An iterable of paths or path strings.
        """
        self._paths = frozenset(PurePosixPath(path) for path in paths)
        for path in self._paths:
            if path.is_absolute():
                raise ValueError(f"Path must be relative: {path}")

    def __repr__(self) -> str:
        return str(self.sorted())

    def __len__(self) -> int:
        return len(self._paths)

    def __bool__(self) -> bool:
        return bool(self._paths)

    def __contains__(self, path: PurePosixPath | str) -> bool:
        return PurePosixPath(path) in self._paths

    def __iter__(self) -> Iterator[PurePosixPath]:
        return iter(self._paths)

    def sorted(self) -> 'KnowledgeRanking':
        """
        Returns a default sorted ranking of the paths in this index.

        The default sorting is pre-order traversal of a lexicographically
        sorted tree.
        """
        from llobot.knowledge.ranking.trees import preorder_lexicographical_ranking
        return preorder_lexicographical_ranking(self)

    def reversed(self) -> 'KnowledgeRanking':
        """
        Returns a reversed default sorted ranking of the paths in this index.
        """
        return self.sorted().reversed()

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> KnowledgeIndex:
        """
        Returns a new index with paths present in both this index and the whitelist.
        """
        whitelist = coerce_subset(whitelist)
        return KnowledgeIndex(path for path in self if path in whitelist)

    def __or__(self, addition: PurePosixPath | KnowledgeIndex) -> KnowledgeIndex:
        """
        Returns a new index with paths from both this index and the addition.
        """
        if isinstance(addition, PurePosixPath):
            return self | KnowledgeIndex([addition])
        if isinstance(addition, KnowledgeIndex):
            return KnowledgeIndex(self._paths | addition._paths)
        raise TypeError

    def __sub__(self, blacklist: KnowledgeSubset | str | KnowledgeIndex | PurePosixPath) -> KnowledgeIndex:
        """
        Returns a new index with paths from this index that are not in the blacklist.
        """
        return self & ~coerce_subset(blacklist)

    def __rtruediv__(self, prefix: PurePosixPath | str) -> KnowledgeIndex:
        """
        Creates a new `KnowledgeIndex` with a prefix prepended to all paths.
        """
        prefix = PurePosixPath(prefix)
        return KnowledgeIndex(prefix/path for path in self)

    def __truediv__(self, subtree: PurePosixPath | str) -> KnowledgeIndex:
        """
        Creates a new `KnowledgeIndex` with a prefix stripped from all paths.

        Only paths within the `subtree` are kept.
        """
        subtree = PurePosixPath(subtree)
        return KnowledgeIndex(path.relative_to(subtree) for path in self if path.is_relative_to(subtree))

type KnowledgeIndexPrecursor = KnowledgeIndex | 'Knowledge' | 'KnowledgeRanking'

def coerce_index(what: KnowledgeIndexPrecursor) -> KnowledgeIndex:
    """
    Coerces various objects into a `KnowledgeIndex`.

    - `KnowledgeIndex` is returned as is.
    - `Knowledge` and `KnowledgeRanking` are converted by extracting their paths.
    """
    if isinstance(what, KnowledgeIndex):
        return what
    from llobot.knowledge import Knowledge
    if isinstance(what, Knowledge):
        return what.keys()
    from llobot.knowledge.ranking import KnowledgeRanking
    if isinstance(what, KnowledgeRanking):
        return KnowledgeIndex(what)
    raise TypeError(what)

__all__ = [
    'KnowledgeIndex',
    'KnowledgeIndexPrecursor',
    'coerce_index',
]
