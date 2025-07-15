from __future__ import annotations
import math
from functools import cache, lru_cache
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.contexts import Context
from llobot.scores.knowledge import KnowledgeScores
from llobot.formatters.knowledge import KnowledgeFormatter
import llobot.knowledge.subsets
import llobot.knowledge.rankings
import llobot.formatters.knowledge
import llobot.scores.knowledge
import llobot.contexts

class KnowledgeCrammer:
    def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores, ranking: KnowledgeRanking) -> Context:
        return llobot.contexts.empty()

    def __call__(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores, ranking: KnowledgeRanking) -> Context:
        return self.cram(knowledge, budget, scores, ranking)

@lru_cache
def priority(*,
    formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
) -> KnowledgeCrammer:
    class PriorityKnowledgeCrammer(KnowledgeCrammer):
        def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores, ranking: KnowledgeRanking) -> Context:
            knowledge &= ranking
            knowledge &= scores
            # Premultiply with document lengths. Both scores and lengths will get a denominator in the loop.
            scores *= llobot.scores.knowledge.length(knowledge)
            while True:
                formatted = formatter(knowledge, ranking)
                length = formatted.cost
                if length <= budget:
                    return formatted
                # Measure density using formatted documents, so that formatting overhead counts into the weight of the document.
                # The code below is a bit optimized. Unoptimized version: (score / sqrt(cost)) * (length / cost).
                # First factor is value density. Square root spreads available budget between document diversity and document length.
                # Hardcoding sqrt here is not good. We need to make this configurable in the future somehow.
                # Second factor is the ratio of actual content to formatter output length. This discourages inclusion of tiny files.
                costs = formatted.knowledge_cost
                density = KnowledgeScores({path: scores[path] * (cost ** -1.5) for path, cost in costs})
                density_ranking = list(llobot.knowledge.rankings.descending(density))
                removed = []
                while length > budget and density_ranking:
                    path = density_ranking[-1]
                    del density_ranking[-1]
                    length -= costs[path]
                    removed.append(path)
                knowledge -= KnowledgeIndex(removed)
    return PriorityKnowledgeCrammer()

@cache
def standard() -> KnowledgeCrammer:
    return priority()

__all__ = [
    'KnowledgeCrammer',
    'priority',
    'standard',
]
