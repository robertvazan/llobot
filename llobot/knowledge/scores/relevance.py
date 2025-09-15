"""
Scorers that assign scores based on relevance to a subset.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import boilerplate_subset, ancillary_subset
from llobot.utils.values import ValueTypeMixin

class PositiveRelevanceScorer(KnowledgeScorer, ValueTypeMixin):
    """
    Assigns a high score to a relevant subset of documents.
    """
    _relevant: KnowledgeSubset
    _blacklist: KnowledgeSubset | None
    _irrelevant_weight: float

    def __init__(self,
        relevant: KnowledgeSubset,
        blacklist: KnowledgeSubset | None = boilerplate_subset(),
        irrelevant_weight: float = 0.1,
    ):
        self._relevant = relevant
        self._blacklist = blacklist
        self._irrelevant_weight = irrelevant_weight

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        scores = {}
        for path in knowledge.keys():
            if self._blacklist and path in self._blacklist:
                continue
            scores[path] = 1.0 if path in self._relevant else self._irrelevant_weight
        return KnowledgeScores(scores)

class NegativeRelevanceScorer(KnowledgeScorer, ValueTypeMixin):
    """
    Assigns a low score to an irrelevant subset of documents.
    """
    _irrelevant: KnowledgeSubset
    _blacklist: KnowledgeSubset | None
    _irrelevant_weight: float

    def __init__(self,
        irrelevant: KnowledgeSubset = ancillary_subset(),
        blacklist: KnowledgeSubset | None = boilerplate_subset(),
        irrelevant_weight: float = 0.1,
    ):
        self._irrelevant = irrelevant
        self._blacklist = blacklist
        self._irrelevant_weight = irrelevant_weight

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        scores = {}
        for path in knowledge.keys():
            if self._blacklist and path in self._blacklist:
                continue
            scores[path] = self._irrelevant_weight if path in self._irrelevant else 1.0
        return KnowledgeScores(scores)

__all__ = [
    'PositiveRelevanceScorer',
    'NegativeRelevanceScorer',
]
