from __future__ import annotations
import math
from functools import cache, lru_cache
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge.rankers import KnowledgeRanker
from llobot.contexts import Context
from llobot.trimmers import Trimmer
from llobot.scores.knowledge import KnowledgeScores
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.formatters.knowledge import KnowledgeFormatter
import llobot.knowledge.subsets
import llobot.knowledge.rankings
import llobot.knowledge.rankers
import llobot.trimmers
import llobot.formatters.knowledge
import llobot.scores.knowledge
import llobot.scorers.knowledge
import llobot.contexts

class KnowledgeCrammer:
    # Context parameter contains already assembled parts of the prompt, whether preceding or following crammer's output.
    def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores | None = None, context: Context = llobot.contexts.empty()) -> Context:
        return llobot.contexts.empty()

@lru_cache
def priority(*,
    # Trimmer is applied to all documents regardless of whether that's necessary to save space.
    trimmer: Trimmer = llobot.trimmers.boilerplate(),
    scorer: KnowledgeScorer = llobot.scorers.knowledge.standard(),
    formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
    ranker: KnowledgeRanker = llobot.knowledge.rankers.standard(),
) -> KnowledgeCrammer:
    class PriorityKnowledgeCrammer(KnowledgeCrammer):
        def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores | None = None, context: Context = llobot.contexts.empty()) -> Context:
            if budget <= 0 or not knowledge or (scores is not None and not scores):
                return llobot.contexts.empty()
            knowledge = knowledge.strip()
            ranking = ranker(knowledge)
            knowledge &= ranking
            scores = scorer.rescore(knowledge, scores) if scores is not None else scorer(knowledge)
            # Remove documents with zero score. Scorer can be thus used to exclude irrelevant documents.
            # To make that work though, rescoring must not distribute score around.
            knowledge &= scores
            knowledge = knowledge.transform(trimmer.trim_fully)
            # Premultiply with document lengths. Both scores and lengths will get a denominator in the loop.
            scores *= llobot.scores.knowledge.length(knowledge)
            prior_knowledge = context.knowledge
            # Remove documents that have exact copies in context.
            knowledge -= llobot.knowledge.subsets.create(lambda path, content: path in prior_knowledge and prior_knowledge[path] == content)
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

@cache
def retrieval() -> KnowledgeCrammer:
    return priority(scorer=llobot.scorers.knowledge.constant())

# Intended to be used for files that are already in the context but they have changed since.
@cache
def updates() -> KnowledgeCrammer:
    # We would ideally want to score relevance, but that's currently not possible, because score parameter is used for filtering.
    return priority(formatter=llobot.formatters.knowledge.updates(), scorer=llobot.scorers.knowledge.constant())

__all__ = [
    'KnowledgeCrammer',
    'priority',
    'standard',
    'retrieval',
    'updates',
]

