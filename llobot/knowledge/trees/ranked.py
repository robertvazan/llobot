from __future__ import annotations
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.trees.builder import KnowledgeTreeBuilder

def ranked_tree(ranking: KnowledgeRanking) -> 'KnowledgeTree':
    """
    Creates a knowledge tree from a ranking by adding all paths in order.

    Args:
        ranking: A ranking of paths to organize into a tree structure.

    Returns:
        A knowledge tree containing all paths from the ranking.
    """
    builder = KnowledgeTreeBuilder()
    for path in ranking:
        builder.add(path)
    return builder.build()

__all__ = [
    'ranked_tree',
]
