from __future__ import annotations
from llobot.chats.builders import ChatBuilder
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.formats.deltas.knowledge import KnowledgeDeltaFormat, standard_knowledge_delta_format
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking.rankers import KnowledgeRanker, standard_ranker
from llobot.knowledge.ranking.sorting import rank_descending
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.length import score_length
from llobot.knowledge.scores.scorers import KnowledgeScorer, standard_scorer
from llobot.knowledge.scores.uniform import uniform_scores
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import blacklist_subset
from llobot.utils.values import ValueTypeMixin

class PrioritizedKnowledgeCrammer(KnowledgeCrammer, ValueTypeMixin):
    """
    A knowledge crammer that prioritizes documents based on scores and ranking.

    It iteratively removes the least valuable documents from a candidate set
    until the formatted output fits within the builder's budget.
    """
    _scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _blacklist: KnowledgeSubset
    _knowledge_delta_format: KnowledgeDeltaFormat

    def __init__(self, *,
        scorer: KnowledgeScorer = standard_scorer(),
        ranker: KnowledgeRanker = standard_ranker(),
        blacklist: KnowledgeSubset = blacklist_subset(),
        knowledge_delta_format: KnowledgeDeltaFormat = standard_knowledge_delta_format(),
    ):
        """
        Creates a new prioritized knowledge crammer.

        Args:
            scorer: Scorer for document relevance.
            ranker: The ranker to establish the document order.
            blacklist: A subset of documents to exclude from the final context.
            knowledge_delta_format: The format for rendering knowledge.
        """
        self._scorer = scorer
        self._ranker = ranker
        self._blacklist = blacklist
        self._knowledge_delta_format = knowledge_delta_format

    def cram(self, builder: ChatBuilder, knowledge: Knowledge) -> KnowledgeIndex:
        """
        Adds the highest-priority documents that fit the budget.
        """
        if builder.unused <= 0:
            return KnowledgeIndex()

        # Score and rank the full knowledge base.
        scores = self._scorer.score(knowledge)
        ranking = self._ranker.rank(knowledge)

        # Apply blacklist before iterative cramming.
        candidate_knowledge = knowledge - self._blacklist

        # Pre-calculate expensive score components.
        weighted_scores = scores * score_length(candidate_knowledge)

        while True:
            builder.mark()
            formatted = self._knowledge_delta_format.render_fresh_chat(candidate_knowledge, ranking)
            builder.add(formatted)

            if builder.unused >= 0:
                return candidate_knowledge.keys()

            builder.undo()
            if not candidate_knowledge:
                return KnowledgeIndex()

            costs = score_length(candidate_knowledge)
            overhead = formatted.cost - costs.total()
            costs += uniform_scores(candidate_knowledge, overhead)
            density = KnowledgeScores({path: weighted_scores[path] * (costs[path] ** -1.5) for path in candidate_knowledge.keys()})
            density_ranking = list(rank_descending(density, initial=ranking & candidate_knowledge))

            removed_path = density_ranking.pop()
            candidate_knowledge -= removed_path

__all__ = [
    'PrioritizedKnowledgeCrammer',
]
