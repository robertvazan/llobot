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
from llobot.knowledge.scores.pagerank import PageRankScorer
from llobot.knowledge.scores.relevance import NegativeRelevanceScorer
from llobot.knowledge.scores.scorers import KnowledgeScorer
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
    _relevance_scorer: KnowledgeScorer
    _graph_scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _blacklist: KnowledgeSubset
    _knowledge_delta_format: KnowledgeDeltaFormat

    def __init__(self, *,
        relevance_scorer: KnowledgeScorer = NegativeRelevanceScorer(),
        graph_scorer: KnowledgeScorer = PageRankScorer(),
        ranker: KnowledgeRanker = standard_ranker(),
        blacklist: KnowledgeSubset = blacklist_subset(),
        knowledge_delta_format: KnowledgeDeltaFormat = standard_knowledge_delta_format(),
    ):
        """
        Creates a new prioritized knowledge crammer.

        Args:
            relevance_scorer: Scorer for initial relevance.
            graph_scorer: Scorer for graph-based relevance (e.g., PageRank).
            ranker: The ranker to establish the document order.
            blacklist: A subset of documents to exclude from the final context.
            knowledge_delta_format: The format for rendering knowledge.
        """
        self._relevance_scorer = relevance_scorer
        self._graph_scorer = graph_scorer
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
        scores = self._relevance_scorer.score(knowledge)
        scores = self._graph_scorer.rescore(knowledge, scores)
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
