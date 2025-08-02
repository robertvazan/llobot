from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset

class UnionKnowledgeSubset(KnowledgeSubset):
    _suffixes: set[str]
    _filenames: set[str]
    _directories: set[str]
    _children: list[KnowledgeSubset]

    def __init__(self, suffixes: set[str] = set(), filenames: set[str] = set(), directories: set[str] = set(), children: Iterable[KnowledgeSubset] = tuple()):
        self._suffixes = suffixes
        self._filenames = filenames
        self._directories = directories
        self._children = tuple(children)

    def contains(self, path: Path) -> bool:
        return (path.suffix in self._suffixes or
                path.name in self._filenames or
                self._directories and any(part in self._directories for part in path.parts) or
                any(path in subset for subset in self._children))

    def __or__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        if isinstance(other, UnionKnowledgeSubset):
            return UnionKnowledgeSubset(
                self._suffixes | other._suffixes,
                self._filenames | other._filenames,
                self._directories | other._directories,
                self._children + other._children
            )
        return UnionKnowledgeSubset(
            self._suffixes,
            self._filenames,
            self._directories,
            self._children + (other,)
        )

def suffix(*suffixes: str) -> UnionKnowledgeSubset:
    return UnionKnowledgeSubset(suffixes=set(suffixes))

def filename(*filenames: str) -> UnionKnowledgeSubset:
    return UnionKnowledgeSubset(filenames=set(filenames))

def directory(*directories: str) -> UnionKnowledgeSubset:
    return UnionKnowledgeSubset(directories=set(directories))

def union(*subsets: KnowledgeSubset) -> UnionKnowledgeSubset:
    return UnionKnowledgeSubset(children=subsets)

__all__ = [
    'UnionKnowledgeSubset',
    'suffix',
    'filename',
    'directory',
    'union',
]
