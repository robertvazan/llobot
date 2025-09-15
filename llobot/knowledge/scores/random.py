"""
Scorers that assign random scores for shuffling.
"""
from __future__ import annotations
from zlib import crc32
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex, coerce_index
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.utils.values import ValueTypeMixin

# This uses only path, not content, so that content changes do not cause cache-killing reorderings.
def random_scores(paths: KnowledgeIndex | KnowledgeRanking | Knowledge | KnowledgeScores) -> KnowledgeScores:
    """
    Assigns a deterministic pseudo-random score to each document based on its path.

    Args:
        paths: The documents to score.

    Returns:
        `KnowledgeScores` with pseudo-random scores.
    """
    paths = coerce_index(paths)
    # Here we have to be careful to avoid zero scores, so that the resulting score object has all the paths.
    return KnowledgeScores({path: crc32(str(path).encode('utf-8')) or 1 for path in paths})

class RandomScorer(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that assigns a deterministic pseudo-random score based on path.
    """

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Assigns pseudo-random scores to all documents in the knowledge.

        Args:
            knowledge: The knowledge base.

        Returns:
            `KnowledgeScores` with pseudo-random scores.
        """
        return random_scores(knowledge)

__all__ = [
    'random_scores',
    'RandomScorer',
]
