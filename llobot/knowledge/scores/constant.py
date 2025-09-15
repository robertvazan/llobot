"""
Scorers that assign a constant score.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex, coerce_index
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.utils.values import ValueTypeMixin

def constant_scores(keys: KnowledgeIndex | KnowledgeRanking | Knowledge | KnowledgeScores, score: float = 1) -> KnowledgeScores:
    """
    Assigns a constant score to each document.

    Args:
        keys: The documents to score.
        score: The constant score to assign.

    Returns:
        A `KnowledgeScores` object with the constant scores.
    """
    keys = coerce_index(keys)
    return KnowledgeScores({path: score for path in keys})

class ConstantScorer(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that assigns a constant score to all documents.
    """
    _score: float

    def __init__(self, score: float = 1):
        """
        Creates a new constant scorer.

        Args:
            score: The constant score to assign.
        """
        self._score = score

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Assigns the constant score to all documents in the knowledge.

        Args:
            knowledge: The knowledge base.

        Returns:
            `KnowledgeScores` with the constant score for all documents.
        """
        return constant_scores(knowledge, self._score)

__all__ = [
    'constant_scores',
    'ConstantScorer',
]
