"""
Base `KnowledgeScorer` and standard scorer implementations.
"""
from __future__ import annotations
from functools import cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset

class KnowledgeScorer:
    """
    Base class for knowledge scoring strategies.

    A scorer defines a method to assign numerical scores to documents in a
    `Knowledge` base.
    """
    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Calculates scores for the given knowledge.

        Args:
            knowledge: The knowledge base to score.

        Returns:
            A `KnowledgeScores` object with scores for documents.
        """
        return KnowledgeScores()

    def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
        """
        Recalculates scores based on an initial set of scores.

        The default implementation multiplies the initial scores by the scores
        from this scorer. Subclasses can override this for more complex logic,
        like score propagation in PageRank.

        Args:
            knowledge: The knowledge base to score.
            initial: The initial scores to start from.

        Returns:
            The new `KnowledgeScores` object.
        """
        return initial * self.score(knowledge)

def coerce_scorer(material: KnowledgeScorer | KnowledgeSubset | str | Path | KnowledgeIndex) -> KnowledgeScorer:
    """
    Coerces various objects into a KnowledgeScorer.

    - `KnowledgeScorer` is returned as is.
    - `KnowledgeSubset` or its coercable types are converted into a `SubsetScorer`.
    """
    if isinstance(material, KnowledgeScorer):
        return material
    from llobot.knowledge.scores.subset import SubsetScorer
    subset = coerce_subset(material)
    return SubsetScorer(subset)

@cache
def standard_scorer() -> KnowledgeScorer:
    """
    Returns the standard knowledge scorer.
    """
    from llobot.knowledge.scores.pagerank import PageRankScorer
    return PageRankScorer()

__all__ = [
    'KnowledgeScorer',
    'coerce_scorer',
    'standard_scorer',
]
