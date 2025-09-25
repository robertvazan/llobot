"""
Defines the `KnowledgeSubset` interface for filtering knowledge paths.

This package provides the `KnowledgeSubset` base class, which represents a
predicate that can be applied to a `pathlib.Path` to determine membership in a
set. It also provides `coerce_subset` to convert various types into subsets.

Implementations of `KnowledgeSubset` for various matching strategies (e.g., by
suffix, filename, pattern) are provided in submodules. Subsets can be combined
using logical operators (`|`, `&`, `-`, `~`).

Submodules
----------
complement
    Inverts a subset.
difference
    Computes the difference between two subsets.
directory
    Matches paths within specific directories.
empty
    An empty subset that matches nothing.
filename
    Matches paths with specific filenames.
fullmatch
    Matches paths against a glob-like pattern matching the whole path.
intersection
    Computes the intersection of two subsets.
parsing
    Parses string patterns and files into subsets.
paths
    A subset defined by an explicit set of paths.
relative
    Matches paths against a glob-like pattern matching a suffix of the path.
solo
    A subset containing a single path.
standard
    Pre-defined subsets for common use cases (e.g., boilerplate, overviews).
suffix
    Matches paths with specific file suffixes.
union
    Computes the union of two or more subsets.
universal
    A subset that matches everything.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable

class KnowledgeSubset:
    """
    A filter for knowledge paths.

    Subsets are predicates that determine whether a given path is part of the
    subset. They can be combined using logical operators (`|`, `&`, `-`, `~`).
    Subsets cache their results for performance.
    """
    _memory: dict[Path, bool]

    def contains(self, path: Path) -> bool:
        """
        Checks if a path is in the subset. Subclasses must implement this.
        """
        raise NotImplementedError

    def __contains__(self, path: Path) -> bool:
        try:
            memory = self._memory
        except AttributeError:
            memory = self._memory = {}
        accepted = memory.get(path, None)
        if accepted is None:
            # We will cache the result forever. There aren't going to be that many different paths.
            memory[path] = accepted = self.contains(path)
        return accepted

    def __or__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        from llobot.knowledge.subsets.union import UnionSubset
        return UnionSubset(self, other)

    def __and__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        from llobot.knowledge.subsets.intersection import IntersectionSubset
        return IntersectionSubset(self, other)

    def __sub__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        from llobot.knowledge.subsets.difference import DifferenceSubset
        return DifferenceSubset(self, other)

    def __invert__(self) -> KnowledgeSubset:
        from llobot.knowledge.subsets.complement import ComplementSubset
        return ComplementSubset(self)

    # For ValueTypeMixin
    def _ephemeral_fields(self) -> Iterable[str]:
        """
        Excludes the internal cache from value-based comparisons.
        """
        return ['_memory']


def coerce_subset(material: KnowledgeSubset | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores' | 'Knowledge') -> KnowledgeSubset:
    """
    Coerces various objects into a KnowledgeSubset.

    - `KnowledgeSubset` is returned as is.
    - `str` is parsed as a glob pattern.
    - `Path` is treated as a subset containing only that path.
    - Knowledge containers (`KnowledgeIndex`, `Knowledge`, etc.) are converted
      to a subset containing their paths.
    """
    if isinstance(material, KnowledgeSubset):
        return material
    if isinstance(material, str):
        from llobot.knowledge.subsets.parsing import parse_pattern
        return parse_pattern(material)
    if isinstance(material, Path):
        from llobot.knowledge.subsets.solo import SoloSubset
        return SoloSubset(material)

    # Use local import to avoid circular dependency
    import llobot.knowledge.indexes
    from llobot.knowledge.subsets.paths import PathsSubset
    from llobot.knowledge.scores import KnowledgeScores
    if isinstance(material, KnowledgeScores):
        index = material.keys()
    else:
        index = llobot.knowledge.indexes.coerce_index(material)
    return PathsSubset(index)


__all__ = [
    'KnowledgeSubset',
    'coerce_subset',
]
