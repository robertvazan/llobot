from __future__ import annotations
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.knowledge.ranking.overviews import OverviewsFirstRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.ranking.sorting import DescendingRanker
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset
from llobot.knowledge.subsets.standard import blacklist_subset
from llobot.utils.values import ValueTypeMixin

def _default_ranker() -> KnowledgeRanker:
    return OverviewsFirstRanker(tiebreaker=DescendingRanker())

class FullKnowledgeCrammer(KnowledgeCrammer, ValueTypeMixin):
    """
    A knowledge crammer that adds all documents into the context.

    It ranks documents to ensure logical order (e.g. overviews first), filters out
    files that are blacklisted or already loaded, and then adds everything else
    to the context regardless of the budget.
    """
    _ranker: KnowledgeRanker
    _blacklist: KnowledgeSubset
    _knowledge_format: KnowledgeFormat

    def __init__(self, *,
        ranker: KnowledgeRanker | None = None,
        blacklist: KnowledgeSubset = blacklist_subset(),
        knowledge_format: KnowledgeFormat = standard_knowledge_format(),
    ):
        """
        Creates a new full knowledge crammer.

        Args:
            ranker: The ranker to establish the document order. Defaults to
                    `OverviewsFirstRanker` over `DescendingRanker`.
            blacklist: A subset of documents to exclude from the final context.
            knowledge_format: The format for rendering knowledge.
        """
        self._ranker = ranker if ranker is not None else _default_ranker()
        self._blacklist = blacklist
        self._knowledge_format = knowledge_format

    def cram(self, env: Environment) -> None:
        """
        Adds all available documents to the context.
        """
        builder = env[ContextEnv].builder
        knowledge = env[ProjectEnv].union.read_all()

        # Rank and apply blacklist and filter out already loaded files.
        already_loaded = coerce_subset(env[KnowledgeEnv].keys())
        ranking = self._ranker.rank(knowledge) - (self._blacklist | already_loaded)

        if not ranking:
            return

        candidate_knowledge = knowledge & ranking
        formatted = self._knowledge_format.render_chat(candidate_knowledge, ranking)
        builder.add(formatted)
        env[KnowledgeEnv].update(candidate_knowledge)

__all__ = [
    'FullKnowledgeCrammer',
]
