"""
A scorer that chains multiple scorers together.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.knowledge.scores.constant import constant_scores
from llobot.utils.values import ValueTypeMixin

class KnowledgeScorerChain(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that applies a sequence of other scorers.

    The `score()` method uses the first scorer's `score()` method to get initial
    scores, then refines them with `rescore()` from the subsequent scorers. The
    `rescore()` method applies `rescore()` from all component scorers to the
    initial scores.
    """
    _scorers: tuple[KnowledgeScorer, ...]

    def __init__(self, *scorers: KnowledgeScorer):
        """
        Creates a new scorer chain.

        Nested chains are flattened.

        Args:
            *scorers: The scorers to chain together.
        """
        flattened = []
        for scorer in scorers:
            if isinstance(scorer, KnowledgeScorerChain):
                flattened.extend(scorer._scorers)
            else:
                flattened.append(scorer)
        self._scorers = tuple(flattened)

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Calculates scores by running the full chain.

        Args:
            knowledge: The knowledge base to score.

        Returns:
            The final `KnowledgeScores`.
        """
        if not self._scorers:
            return constant_scores(knowledge)
        scores = self._scorers[0].score(knowledge)
        for scorer in self._scorers[1:]:
            scores = scorer.rescore(knowledge, scores)
        return scores

    def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
        """
        Recalculates scores by running the full chain on initial scores.

        Args:
            knowledge: The knowledge base to score.
            initial: The initial scores to start from.

        Returns:
            The new `KnowledgeScores`.
        """
        scores = initial
        for scorer in self._scorers:
            scores = scorer.rescore(knowledge, scores)
        return scores

__all__ = [
    'KnowledgeScorerChain',
]
