"""
Functions for score normalization.
"""
from __future__ import annotations
from llobot.knowledge.scores import KnowledgeScores

def normalize_scores(denormalized: KnowledgeScores, budget: float = 1) -> KnowledgeScores:
    """
    Normalizes scores to sum up to a given budget.

    If the total of denormalized scores is zero, the original scores are
    returned.

    Args:
        denormalized: The scores to normalize.
        budget: The target total for the normalized scores.

    Returns:
        The normalized scores.
    """
    total = denormalized.total()
    if not total:
        return denormalized
    return (budget / total) * denormalized

__all__ = [
    'normalize_scores',
]
