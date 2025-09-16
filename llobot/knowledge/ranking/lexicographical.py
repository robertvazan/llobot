"""
Rankers that sort documents lexicographically.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import coerce_index
from llobot.knowledge.ranking import KnowledgeRanking, KnowledgeRankingPrecursor
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.utils.values import ValueTypeMixin

def rank_lexicographically(index: KnowledgeRankingPrecursor) -> KnowledgeRanking:
    """
    Creates a knowledge ranking by sorting paths lexicographically.

    Args:
        index: Knowledge index or its precursor to convert to a ranking.

    Returns:
        A lexicographically sorted knowledge ranking.
    """
    index = coerce_index(index)
    return KnowledgeRanking(sorted(index))

class LexicographicalRanker(KnowledgeRanker, ValueTypeMixin):
    """
    A ranker that sorts documents lexicographically.
    """
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        """
        Ranks documents in the knowledge base lexicographically.

        Args:
            knowledge: The knowledge base to rank.

        Returns:
            A lexicographically sorted ranking.
        """
        return rank_lexicographically(knowledge)

__all__ = [
    'rank_lexicographically',
    'LexicographicalRanker',
]
