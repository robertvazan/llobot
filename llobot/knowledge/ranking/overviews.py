"""
Rankers that prioritize overview documents.

This module provides a ranker that reorders a knowledge ranking to prioritize
overview files by placing them before other files from the same directory or
its subdirectories.
"""
from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking, KnowledgeRankingPrecursor, coerce_ranking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.ranking.trees import PreorderRanker
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.knowledge.trees.ranked import ranked_tree
from llobot.utils.values import ValueTypeMixin

def rank_overviews_first(
    initial: KnowledgeRankingPrecursor,
    *,
    overviews: KnowledgeSubset | None = None
) -> KnowledgeRanking:
    """
    Reorders a ranking to ensure all ancestor overviews precede a document.

    For each document in the initial ranking, this function ensures that all
    overview files from its ancestor directories (from root to the document's
    own directory) are included in the output before the document itself.

    Args:
        initial: The initial ranking to reorder.
        overviews: Subset defining overview files. Defaults to the standard one.

    Returns:
        A new ranking with ancestor overviews prepended.
    """
    if overviews is None:
        overviews = overviews_subset()
    ranking = coerce_ranking(initial)
    overview_docs = [path for path in ranking if path in overviews]
    overview_tree = ranked_tree(KnowledgeRanking(overview_docs))

    result = []
    seen = set()
    for path in ranking:
        # Add parent overviews first, from root down to the file's directory.
        for parent in reversed(path.parents):
            parent_tree = overview_tree[parent]
            for overview in parent_tree.file_paths:
                if overview not in seen:
                    result.append(overview)
                    seen.add(overview)

        # Add the document itself if it has not been already added (e.g. it's an overview).
        if path not in seen:
            result.append(path)
            seen.add(path)

    return KnowledgeRanking(result)

class OverviewsFirstRanker(KnowledgeRanker, ValueTypeMixin):
    """
    A ranker that ensures all ancestor overviews precede a document.
    """
    _tiebreaker: KnowledgeRanker
    _overviews: KnowledgeSubset

    def __init__(self, *,
        tiebreaker: KnowledgeRanker = PreorderRanker(tiebreaker=LexicographicalRanker()),
        overviews: KnowledgeSubset | None = None
    ):
        """
        Creates a new `OverviewsFirstRanker`.

        Args:
            tiebreaker: The ranker used to create the initial ordering before
                        overview prioritization. Defaults to a pre-order
                        lexicographical ranker.
            overviews: The subset defining which files are overviews.
                       Defaults to the standard one.
        """
        self._tiebreaker = tiebreaker
        self._overviews = overviews if overviews is not None else overviews_subset()

    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        """
        Ranks the knowledge, ensuring ancestor overviews are prepended.

        Args:
            knowledge: The knowledge base to rank.

        Returns:
            The final, reordered ranking.
        """
        initial = self._tiebreaker.rank(knowledge)
        return rank_overviews_first(initial, overviews=self._overviews)

__all__ = [
    'rank_overviews_first',
    'OverviewsFirstRanker',
]
