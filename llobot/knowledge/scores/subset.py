"""
Scorer for an explicit subset of documents.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.utils.values import ValueTypeMixin

class SubsetScorer(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that assigns a constant score to documents in a given subset.
    """
    _subset: KnowledgeSubset
    _score: float

    def __init__(self, subset: KnowledgeSubset, score: float = 1.0):
        """
        Creates a new subset scorer.

        Args:
            subset: The subset of documents to score.
            score: The score to assign to documents in the subset.
        """
        self._subset = subset
        self._score = score

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Assigns the score to documents in the subset that are also in the knowledge.

        Args:
            knowledge: The knowledge base.

        Returns:
            `KnowledgeScores` with scores assigned.
        """
        from llobot.knowledge.scores.constant import constant_scores
        return constant_scores(knowledge & self._subset, self._score)

__all__ = [
    'SubsetScorer',
]
