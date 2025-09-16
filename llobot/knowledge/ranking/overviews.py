"""
Rankers that prioritize overview documents.
"""
from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking, KnowledgeRankingPrecursor, coerce_ranking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.ranking.trees import preorder_ranking
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.knowledge.trees import ranked_tree
from llobot.utils.values import ValueTypeMixin

def rank_overviews_before_everything(
    initial: KnowledgeRankingPrecursor,
    *,
    overviews: KnowledgeSubset | None = None
) -> KnowledgeRanking:
    """
    Reorders a ranking to place all overview files at the beginning.

    The relative order within overviews and within regular files is preserved.

    Args:
        initial: The initial ranking to reorder.
        overviews: Subset defining overview files. Defaults to the standard one.

    Returns:
        A new ranking with all overviews moved to the front.
    """
    if overviews is None:
        overviews = overviews_subset()
    ranking = coerce_ranking(initial)
    overview_docs = [path for path in ranking if path in overviews]
    regular_docs = [path for path in ranking if path not in overviews]
    return KnowledgeRanking(overview_docs + regular_docs)

def rank_overviews_before_siblings(
    initial: KnowledgeRankingPrecursor,
    *,
    overviews: KnowledgeSubset | None = None
) -> KnowledgeRanking:
    """
    Reorders a ranking to place overview files before their siblings.

    This is achieved by first moving all overviews to the front, then
    constructing a directory tree from that order, and finally performing a
    pre-order traversal of the tree to get the final ranking.

    Args:
        initial: The initial ranking to reorder.
        overviews: Subset defining overview files. Defaults to the standard one.

    Returns:
        A new ranking with overviews prioritized within their directories.
    """
    ranking = rank_overviews_before_everything(initial, overviews=overviews)
    tree = ranked_tree(ranking)
    return preorder_ranking(tree)

def rank_overviews_before_document(
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

class OverviewsBeforeSiblingsRanker(KnowledgeRanker, ValueTypeMixin):
    """
    A ranker that places overview files before their siblings in each directory.
    """
    _previous: KnowledgeRanker
    _overviews: KnowledgeSubset

    def __init__(self, *,
        previous: KnowledgeRanker = LexicographicalRanker(),
        overviews: KnowledgeSubset | None = None
    ):
        """
        Creates a new `OverviewsBeforeSiblingsRanker`.

        Args:
            previous: The ranker used to create the initial ordering before
                      overview prioritization. Defaults to `LexicographicalRanker`.
            overviews: The subset defining which files are overviews.
                       Defaults to the standard one.
        """
        self._previous = previous
        self._overviews = overviews if overviews is not None else overviews_subset()

    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        """
        Ranks the knowledge, prioritizing overviews before siblings.

        Args:
            knowledge: The knowledge base to rank.

        Returns:
            The final, reordered ranking.
        """
        initial = self._previous.rank(knowledge)
        return rank_overviews_before_siblings(initial, overviews=self._overviews)

__all__ = [
    'rank_overviews_before_everything',
    'rank_overviews_before_siblings',
    'rank_overviews_before_document',
    'OverviewsBeforeSiblingsRanker',
]
