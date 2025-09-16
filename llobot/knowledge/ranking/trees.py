"""
Ranking functions related to knowledge trees.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.trees import KnowledgeTree, coerce_tree

def preorder_ranking(tree: KnowledgeTree | KnowledgeRanking | KnowledgeIndex | Knowledge) -> KnowledgeRanking:
    """
    Creates a ranking by performing a pre-order traversal of a knowledge tree.

    Args:
        tree: The tree or tree precursor to traverse.

    Returns:
        A `KnowledgeRanking` of paths in pre-order.
    """
    tree = coerce_tree(tree)
    return KnowledgeRanking(tree.all_paths)

__all__ = [
    'preorder_ranking',
]
