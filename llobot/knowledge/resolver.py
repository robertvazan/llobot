"""
Index for efficient, proximity-based path resolution.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from llobot.knowledge.indexes import KnowledgeIndex, KnowledgeIndexPrecursor, coerce_index

@lru_cache(maxsize=2)
def _cached_knowledge_resolver(index: KnowledgeIndex) -> 'KnowledgeResolver':
    """
    Cached constructor for `KnowledgeResolver`.
    """
    return KnowledgeResolver(index)

def cached_knowledge_resolver(index: KnowledgeIndexPrecursor) -> 'KnowledgeResolver':
    """
    Creates a knowledge resolver from a knowledge index or its precursor.

    The resolver is cached for performance.

    Args:
        index: The knowledge index to create a resolver from.
               Can be a `KnowledgeIndex`, `Knowledge`, or `KnowledgeRanking`.

    Returns:
        A `KnowledgeResolver` for efficient path lookups.
    """
    return _cached_knowledge_resolver(coerce_index(index))

class KnowledgeResolver:
    """
    Index for efficient path resolution, with disambiguation based on source
    path proximity.
    """
    _names: dict[str, set[Path]]
    _tails: dict[Path, set[Path]]

    def __init__(self, index: KnowledgeIndex):
        """
        Creates a resolver from a knowledge index.

        Args:
            index: The knowledge index to build the resolver from.
        """
        self._names = {}
        self._tails = {}

        for path in index:
            # Reject paths with no segments
            if not path.parts:
                continue

            # Build _names mapping
            name = path.name
            if name not in self._names:
                self._names[name] = set()
            self._names[name].add(path)

            # Build _tails mapping (last two segments)
            parts = path.parts
            if len(parts) >= 2:
                tail = Path(*parts[-2:])
                if tail not in self._tails:
                    self._tails[tail] = set()
                self._tails[tail].add(path)

    def resolve_all(self, *targets: Path) -> KnowledgeIndex:
        """
        Resolves abbreviated paths to all possible full target paths.

        This method finds all paths in the index that could be referred to by
        the given abbreviated target paths. Disambiguation is not performed.

        Args:
            *targets: The abbreviated paths to resolve.

        Returns:
            A `KnowledgeIndex` of all matching full paths.
        """
        if not targets:
            return KnowledgeIndex()
        candidates = []
        for target in targets:
            # Reject paths with no segments
            if not target.parts:
                continue
            # Determine which lookup table to use and get candidates
            if len(target.parts) == 1:
                # Just a filename, use _names (no filtering needed)
                candidates.extend(list(self._names.get(target.name, set())))
            else:
                # Multi-part path, use _tails with last two segments
                tail = Path(*target.parts[-2:]) if len(target.parts) >= 2 else target
                potentials = self._tails.get(tail, set())
                # Filter candidates to ensure right side matches abbreviated path exactly
                for potential in potentials:
                    candidate_parts = potential.parts
                    target_parts = target.parts
                    if len(candidate_parts) >= len(target_parts):
                        if candidate_parts[-len(target_parts):] == target_parts:
                            candidates.append(potential)
        return KnowledgeIndex(candidates)

    def resolve(self, *targets: Path) -> Path | None:
        """
        Resolves abbreviated paths to a single full target path.

        This is a convenience wrapper around `resolve_all`. If `resolve_all`
        finds exactly one match, that path is returned. Otherwise, `None` is
        returned.

        Args:
            *targets: The abbreviated paths to resolve.

        Returns:
            The resolved full path, or `None` if resolution fails or is ambiguous.
        """
        results = self.resolve_all(*targets)
        if len(results) == 1:
            return list(results)[0]
        return None

    def resolve_all_near(self, source: Path, *targets: Path) -> KnowledgeIndex:
        """
        Resolves abbreviated paths, disambiguating by proximity to a source path.

        This method first finds all possible matches using `resolve_all`. If
        multiple matches are found, it selects the one(s) with the longest
        common path prefix with the `source` path.

        Args:
            source: The source path for disambiguation.
            *targets: The abbreviated paths to resolve.

        Returns:
            A `KnowledgeIndex` of the best-matching full paths. This may contain
            more than one path if there is a tie.
        """
        candidates = self.resolve_all(*targets)
        if len(candidates) <= 1:
            return candidates
        ranking = list(candidates)
        best_target = max(ranking, key=lambda target: self._common_prefix_length(source, target))
        best_prefix_length = self._common_prefix_length(source, best_target)
        tied_targets = [t for t in ranking if self._common_prefix_length(source, t) == best_prefix_length]
        return KnowledgeIndex(tied_targets)

    def resolve_near(self, source: Path, *targets: Path) -> Path | None:
        """
        Resolves abbreviated paths to a single full path, using proximity.

        This is a convenience wrapper around `resolve_all_near`. If it returns
        exactly one path, that path is returned. Otherwise, `None` is returned.

        Args:
            source: The source path for disambiguation.
            *targets: The abbreviated paths to resolve.

        Returns:
            The resolved full path, or `None` if resolution fails or is ambiguous.
        """
        results = self.resolve_all_near(source, *targets)
        if len(results) == 1:
            return list(results)[0]
        return None

    @staticmethod
    def _common_prefix_length(path1: Path, path2: Path) -> int:
        """
        Returns the length of the common prefix between two paths.
        """
        parts1 = path1.parts
        parts2 = path2.parts
        length = 0
        for p1, p2 in zip(parts1, parts2):
            if p1 == p2:
                length += 1
            else:
                break
        return length

__all__ = [
    'KnowledgeResolver',
    'cached_knowledge_resolver',
]
