"""
Scorers that distribute a total score budget uniformly.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex, KnowledgeIndexPrecursor, coerce_index
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.knowledge.scores.constant import constant_scores
from llobot.utils.values import ValueTypeMixin

def uniform_scores(keys: KnowledgeIndexPrecursor, budget: float = 1) -> KnowledgeScores:
    """
    Distributes a score budget uniformly among all documents.

    Args:
        keys: The documents to score. Can be a `KnowledgeIndex`, `Knowledge`, or `KnowledgeRanking`.
        budget: The total score budget to distribute.

    Returns:
        A `KnowledgeScores` object with uniform scores.
    """
    keys = coerce_index(keys)
    return constant_scores(keys, budget / len(keys)) if keys else KnowledgeScores()

class UniformScorer(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that distributes a score budget uniformly among all documents.
    """
    _budget: float

    def __init__(self, budget: float = 1):
        """
        Creates a new uniform scorer.

        Args:
            budget: The total score budget to distribute.
        """
        self._budget = budget

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Distributes the score budget uniformly among all documents in the knowledge.

        Args:
            knowledge: The knowledge base.

        Returns:
            `KnowledgeScores` with uniform scores.
        """
        return uniform_scores(knowledge, self._budget)

__all__ = [
    'uniform_scores',
    'UniformScorer',
]
