"""
Ranking functions and rankers related to knowledge trees.

This module provides ways to create rankings by traversing a `KnowledgeTree`.
The primary method is pre-order traversal, which lists a directory's files
before descending into its subdirectories.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.trees import KnowledgeTree, coerce_tree
from llobot.utils.values import ValueTypeMixin

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

class PreorderRanker(KnowledgeRanker, ValueTypeMixin):
    """
    A ranker that creates a ranking by performing a pre-order traversal of a
    knowledge tree. The tree itself is built from an initial ranking.
    """
    _tiebreaker: KnowledgeRanker

    def __init__(self, *, tiebreaker: KnowledgeRanker = LexicographicalRanker()):
        """
        Creates a new `PreorderRanker`.

        Args:
            tiebreaker: The ranker used to create the initial ordering from which
                        the tree is built. Defaults to `LexicographicalRanker`.
        """
        self._tiebreaker = tiebreaker

    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        """
        Ranks the knowledge by building a tree and traversing it in pre-order.

        Args:
            knowledge: The knowledge base to rank.

        Returns:
            A `KnowledgeRanking` of paths in pre-order.
        """
        initial = self._tiebreaker.rank(knowledge)
        return preorder_ranking(initial)

__all__ = [
    'preorder_ranking',
    'PreorderRanker',
]
