"""
Scorers based on document length.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.utils.values import ValueTypeMixin

def score_length(knowledge: Knowledge) -> KnowledgeScores:
    """
    Assigns a score equal to the length of the document content.

    Args:
        knowledge: The knowledge base.

    Returns:
        `KnowledgeScores` with scores equal to document lengths.
    """
    return KnowledgeScores({path: len(content) for path, content in knowledge})

class LengthScorer(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that assigns a score equal to the length of the document content.
    """

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Scores documents by their length.

        Args:
            knowledge: The knowledge base.

        Returns:
            `KnowledgeScores` where each score is the document's length.
        """
        return score_length(knowledge)

__all__ = [
    'score_length',
    'LengthScorer',
]
