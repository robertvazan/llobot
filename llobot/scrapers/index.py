from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex, coerce_index
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.scores import KnowledgeScores

class ScrapingIndex:
    """
    Index for efficient path resolution during scraping.

    Provides fast lookup of abbreviated paths to full paths, with disambiguation
    based on source path proximity.
    """
    _names: dict[str, set[Path]]
    _tails: dict[Path, set[Path]]

    def __init__(self, index: KnowledgeIndex):
        """
        Creates a scraping index from a knowledge index.

        Args:
            index: The knowledge index to build the scraping index from
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

    def lookup(self, source: Path, *abbreviated: Path) -> Path | None:
        """
        Resolves abbreviated paths to a full target path.

        Args:
            source: The source path for disambiguation
            *abbreviated: The abbreviated paths to resolve (merged candidates)

        Returns:
            The resolved full path, or None if resolution fails or is ambiguous
        """
        if not abbreviated:
            return None

        targets = []

        for abbrev in abbreviated:
            # Reject paths with no segments
            if not abbrev.parts:
                continue

            # Determine which lookup table to use and get candidates
            if len(abbrev.parts) == 1:
                # Just a filename, use _names (no filtering needed)
                targets.extend(list(self._names.get(abbrev.name, set())))
            else:
                # Multi-part path, use _tails with last two segments
                tail = Path(*abbrev.parts[-2:]) if len(abbrev.parts) >= 2 else abbrev
                candidates = self._tails.get(tail, set())

                # Filter candidates to ensure right side matches abbreviated path exactly
                for candidate in candidates:
                    candidate_parts = candidate.parts
                    abbreviated_parts = abbrev.parts
                    if len(candidate_parts) >= len(abbreviated_parts):
                        if candidate_parts[-len(abbreviated_parts):] == abbreviated_parts:
                            targets.append(candidate)

        targets = list(set(targets))

        if not targets:
            return None

        if len(targets) == 1:
            return targets[0]

        # Multiple targets, find the one closest to source (longest common prefix)
        best_target = max(targets, key=lambda target: self._common_prefix_length(source, target))

        # Check if there are multiple targets with the same best prefix length
        best_prefix_length = self._common_prefix_length(source, best_target)
        tied_targets = [t for t in targets if self._common_prefix_length(source, t) == best_prefix_length]

        return None if len(tied_targets) > 1 else best_target

    @staticmethod
    def _common_prefix_length(path1: Path, path2: Path) -> int:
        """
        Returns the length of the common prefix between two paths.

        Args:
            path1: First path
            path2: Second path

        Returns:
            The number of common leading path segments
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

@lru_cache(maxsize=2)
def _create_scraping_index(index: KnowledgeIndex) -> ScrapingIndex:
    return ScrapingIndex(index)

def create_scraping_index(index: KnowledgeIndex | Knowledge | KnowledgeRanking | KnowledgeScores) -> ScrapingIndex:
    """
    Creates a scraping index from knowledge index.

    Args:
        index: The knowledge index to create an scraping index from, or its precursor

    Returns:
        A scraping index for efficient path lookups
    """
    return _create_scraping_index(coerce_index(index))

__all__ = [
    'ScrapingIndex',
    'create_scraping_index',
]
