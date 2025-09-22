from __future__ import annotations
from llobot.knowledge.ranking import KnowledgeRankingPrecursor
from llobot.knowledge.ranking.lexicographical import rank_lexicographically
from llobot.knowledge.trees.ranked import ranked_tree

def lexicographical_tree(index: KnowledgeRankingPrecursor) -> 'KnowledgeTree':
    """
    Creates a knowledge tree from an index or index precursor, sorted lexicographically.

    Args:
        index: Knowledge index or its precursor to convert to a tree.

    Returns:
        A knowledge tree with paths sorted lexicographically.
    """
    ranking = rank_lexicographically(index)
    return ranked_tree(ranking)

__all__ = [
    'lexicographical_tree',
]
