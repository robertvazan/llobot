from __future__ import annotations
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.overviews import OverviewsFirstRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.ranking.sorting import DescendingRanker
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import blacklist_subset
from llobot.utils.values import ValueTypeMixin

def _default_ranker() -> KnowledgeRanker:
    return OverviewsFirstRanker(tiebreaker=DescendingRanker())

class RankedKnowledgeCrammer(KnowledgeCrammer, ValueTypeMixin):
    """
    A knowledge crammer that adds documents in a ranked order until the budget is filled.

    It first ranks all documents, then adds as many as possible from the top of the
    ranking that fit within the provided budget. The process is iterative:
    it formats a selection, checks if it fits, and if not, removes documents
    from the end of the selection and tries again.
    """
    _ranker: KnowledgeRanker
    _blacklist: KnowledgeSubset
    _knowledge_format: KnowledgeFormat
    _budget: int

    def __init__(self, *,
        ranker: KnowledgeRanker | None = None,
        blacklist: KnowledgeSubset = blacklist_subset(),
        knowledge_format: KnowledgeFormat = standard_knowledge_format(),
        budget: int = 50_000,
    ):
        """
        Creates a new ranked knowledge crammer.

        Args:
            ranker: The ranker to establish the document order. Defaults to
                    `OverviewsFirstRanker` over `DescendingRanker`.
            blacklist: A subset of documents to exclude from the final context.
            knowledge_format: The format for rendering knowledge.
            budget: The character budget for context stuffing.
        """
        self._ranker = ranker if ranker is not None else _default_ranker()
        self._blacklist = blacklist
        self._knowledge_format = knowledge_format
        self._budget = budget

    def cram(self, env: Environment) -> None:
        """
        Adds the highest-ranked documents that fit the budget.
        """
        builder = env[ContextEnv].builder
        initial_mark = builder.mark()

        knowledge = env[ProjectEnv].union.read_all()

        if self._budget <= 0:
            return

        # Rank and apply blacklist.
        ranking = self._ranker.rank(knowledge) - self._blacklist

        # Phase 1: Initial selection based on raw content size.
        # This is a rough first pass that ignores formatting overhead.
        selection_paths = []
        cost = 0
        for path in ranking:
            doc_cost = len(knowledge[path])
            if cost + doc_cost > self._budget:
                break
            cost += doc_cost
            selection_paths.append(path)

        if not selection_paths:
            return

        # Phase 2: Iteratively refine selection to account for formatting overhead.
        while True:
            selection_ranking = KnowledgeRanking(selection_paths)
            candidate_knowledge = knowledge & selection_ranking

            trial_mark = builder.mark()
            formatted = self._knowledge_format.render_chat(candidate_knowledge, selection_ranking)
            builder.add(formatted)

            remaining = builder.remaining(initial_mark, self._budget)
            if remaining >= 0:
                env[KnowledgeEnv].update(candidate_knowledge)
                return

            overrun = -remaining
            builder.undo(trial_mark)

            # Remove documents from the end of the selection until we've removed
            # enough content to likely cover the overrun.
            removed_cost = 0
            while removed_cost < overrun and selection_paths:
                removed_path = selection_paths.pop()
                removed_cost += len(knowledge[removed_path])

            if not selection_paths:
                return

__all__ = [
    'RankedKnowledgeCrammer',
]
