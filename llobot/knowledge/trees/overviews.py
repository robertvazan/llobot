from __future__ import annotations
from llobot.knowledge.ranking import KnowledgeRankingPrecursor, coerce_ranking
from llobot.knowledge.ranking.overviews import rank_overviews_before_everything
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.trees.ranked import ranked_tree

def overviews_first_tree(
    ranking: KnowledgeRankingPrecursor,
    *,
    overviews: KnowledgeSubset | None = None
) -> 'KnowledgeTree':
    """
    Creates a knowledge tree with overview files listed first.

    This is achieved by reordering the ranking to place all overview files at
    the beginning, and then building a tree from that ranking. This does not
    guarantee that overview files will appear before other files in the same
    directory, but rather that all overview files will be processed first when
    building the tree.

    Args:
        ranking: Knowledge ranking or its precursor to convert to a tree.
        overviews: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A knowledge tree with overview files prioritized.
    """
    ranking = coerce_ranking(ranking)
    ranking = rank_overviews_before_everything(ranking, overviews=overviews)
    return ranked_tree(ranking)

__all__ = [
    'overviews_first_tree',
]
