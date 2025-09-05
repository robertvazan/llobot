from __future__ import annotations
import math
from functools import cache, lru_cache
from llobot.chats.branches import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking, rank_descending
from llobot.knowledge.scores import KnowledgeScores, score_length, uniform_scores
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format

class KnowledgeCrammer:
    def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores, ranking: KnowledgeRanking) -> tuple[ChatBranch, KnowledgeIndex]:
        return ChatBranch(), KnowledgeIndex()

    def __call__(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores, ranking: KnowledgeRanking) -> tuple[ChatBranch, KnowledgeIndex]:
        return self.cram(knowledge, budget, scores, ranking)

@lru_cache
def prioritized_knowledge_crammer(*,
    knowledge_format: KnowledgeFormat = standard_knowledge_format(),
) -> KnowledgeCrammer:
    class PrioritizedKnowledgeCrammer(KnowledgeCrammer):
        def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores, ranking: KnowledgeRanking) -> tuple[ChatBranch, KnowledgeIndex]:
            knowledge &= ranking
            knowledge &= scores
            # Premultiply with document lengths. Both scores and lengths will get a denominator in the loop.
            scores *= score_length(knowledge)
            while True:
                formatted = knowledge_format.render_fresh(knowledge, ranking)
                length = formatted.cost
                if length <= budget:
                    return formatted, knowledge.keys()
                # Measure density using formatted documents, so that formatting overhead counts into the weight of the document.
                # The code below is a bit optimized. Unoptimized version: (score / sqrt(cost)) * (length / cost).
                # First factor is value density. Square root spreads available budget between document diversity and document length.
                # Hardcoding sqrt here is not good. We need to make this configurable in the future somehow.
                # Second factor is the ratio of actual content to formatter output length. This discourages inclusion of tiny files.
                costs = score_length(knowledge)
                overhead = formatted.cost - costs.total()
                costs += uniform_scores(knowledge, overhead)
                density = KnowledgeScores({path: scores[path] * (costs[path] ** -1.5) for path in knowledge.keys()})
                density_ranking = list(rank_descending(density))
                removed = []
                while length > budget and density_ranking:
                    path = density_ranking[-1]
                    del density_ranking[-1]
                    length -= costs[path]
                    removed.append(path)
                knowledge -= KnowledgeIndex(removed)
    return PrioritizedKnowledgeCrammer()

@cache
def standard_knowledge_crammer() -> KnowledgeCrammer:
    return prioritized_knowledge_crammer()

__all__ = [
    'KnowledgeCrammer',
    'prioritized_knowledge_crammer',
    'standard_knowledge_crammer',
]
