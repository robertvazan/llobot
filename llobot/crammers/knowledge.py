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
def trimming(*,
    # Eager trimmer is applied to all documents regardless of whether that's necessary to save space.
    eager_trimmer: Trimmer = llobot.trimmers.eager(),
    # Regular trimmer is used only when we need to save space. It is terminated automatically.
    trimmer: Trimmer = llobot.trimmers.none(),
    scorer: KnowledgeScorer = llobot.scorers.knowledge.standard(),
    formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
    ranker: KnowledgeRanker = llobot.knowledge.rankers.standard(),
) -> KnowledgeCrammer:
    class TrimmingKnowledgeCrammer(KnowledgeCrammer):
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
            knowledge = knowledge.transform(eager_trimmer.trim_fully)
            terminated_trimmer = trimmer.terminate()
            prior_knowledge = context.knowledge
            while True:
                # Remove documents that have exact copies in context.
                knowledge -= llobot.knowledge.subsets.create(lambda path, content: path in prior_knowledge and prior_knowledge[path] == content)
                formatted = formatter(knowledge, ranking)
                if formatted.cost <= budget:
                    return formatted
                # Measure density using formatted documents, so that formatting overhead counts into the weight of the document.
                # Compute square root to invest available budget evenly to both document diversity and document length (which minimizes per-document overhead).
                # Document length transform should be configurable via crammer parameters or we should support arbitrary scorer (augmented with formatter overhead).
                # Scale by ratio of actual content to formatter output length to discourage inclusion of tiny files.
                cost = formatted.knowledge_cost
                density = scores / cost.transform(math.sqrt) * (llobot.scores.knowledge.length(knowledge) / cost)
                density_ranking = list(llobot.knowledge.rankings.descending(density))
                worst = set(density_ranking[:len(density_ranking)//10+1])
                trimmed = Knowledge({path: (terminated_trimmer(path, content) if path in worst else content) for path, content in knowledge})
                if trimmed.cost >= knowledge.cost:
                    raise RuntimeError('Trimmer failed to reduce size of the knowledge.')
                knowledge = trimmed
    return TrimmingKnowledgeCrammer()

@lru_cache
def whole(*,
    # Eager trimmer is applied to all documents regardless of whether that's necessary to save space.
    eager_trimmer: Trimmer = llobot.trimmers.eager(),
    scorer: KnowledgeScorer = llobot.scorers.knowledge.standard(),
    formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
    ranker: KnowledgeRanker = llobot.knowledge.rankers.standard(),
) -> KnowledgeCrammer:
    class WholeKnowledgeCrammer(KnowledgeCrammer):
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
            knowledge = knowledge.transform(eager_trimmer.trim_fully)
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
    return WholeKnowledgeCrammer()

@cache
def standard() -> KnowledgeCrammer:
    return whole()

@cache
def retrieval() -> KnowledgeCrammer:
    return whole(scorer=llobot.scorers.knowledge.constant())

# Intended to be used for files that are already in the context but they have changed since.
@cache
def sync() -> KnowledgeCrammer:
    # We would ideally want to score relevance, but that's currently not possible, because score parameter is used for filtering.
    return whole(formatter=llobot.formatters.knowledge.updates(), scorer=llobot.scorers.knowledge.constant())

__all__ = [
    'KnowledgeCrammer',
    'trimming',
    'whole',
    'standard',
    'retrieval',
    'sync',
]

