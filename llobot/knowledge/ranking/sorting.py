"""
Rankers that sort documents based on scores.
"""
from __future__ import annotations
from llobot.knowledge.ranking import KnowledgeRanking, KnowledgeRankingPrecursor, coerce_ranking
from llobot.knowledge.scores import KnowledgeScores

def rank_ascending(scores: KnowledgeScores, *, initial: KnowledgeRankingPrecursor | None = None) -> KnowledgeRanking:
    """
    Sorts a ranking in ascending order of scores.

    If an initial ranking is provided, it is sorted. Otherwise, a new
    lexicographically sorted ranking of the scored documents is created
    and then sorted by score.

    Args:
        scores: The scores to use for sorting.
        initial: An optional initial ranking to sort.

    Returns:
        A new ranking sorted by score in ascending order.
    """
    if initial is None:
        ranking = coerce_ranking(scores.keys())
    else:
        ranking = coerce_ranking(initial)
    # Sort by score. The original order is used as a tie-breaker because
    # Python's sort is stable.
    return KnowledgeRanking(sorted(ranking, key=lambda path: scores[path]))

def rank_descending(scores: KnowledgeScores, *, initial: KnowledgeRankingPrecursor | None = None) -> KnowledgeRanking:
    """
    Sorts a ranking in descending order of scores.

    This is a convenience function that calls `rank_ascending` with negated scores.

    Args:
        scores: The scores to use for sorting.
        initial: An optional initial ranking to sort.

    Returns:
        A new ranking sorted by score in descending order.
    """
    return rank_ascending(-scores, initial=initial)

__all__ = [
    'rank_ascending',
    'rank_descending',
]
