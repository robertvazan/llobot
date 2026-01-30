"""
A crammer that includes overview files directly under project prefixes.
"""
from __future__ import annotations
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.subsets import coerce_subset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.projects.items import ProjectFile
from llobot.utils.values import ValueTypeMixin

class RootKnowledgeCrammer(KnowledgeCrammer, ValueTypeMixin):
    """
    A knowledge crammer that includes overview files directly under project prefixes.

    This crammer ignores the budget and always adds the selected files. It scans
    the immediate children of all project prefixes, filters them using the standard
    overviews subset, and adds them to the context in lexicographical order.
    """
    _knowledge_format: KnowledgeFormat

    def __init__(self, *,
        knowledge_format: KnowledgeFormat | None = None,
    ):
        """
        Creates a new root knowledge crammer.

        Args:
            knowledge_format: The format for rendering knowledge.
        """
        if knowledge_format is None:
            knowledge_format = standard_knowledge_format()
        self._knowledge_format = knowledge_format

    def cram(self, env: Environment) -> None:
        """
        Adds root overview files to the context.
        """
        builder = env[ContextEnv].builder
        project = env[ProjectEnv].union

        # Collect all immediate children of all prefixes
        candidates = {}
        overviews = overviews_subset()

        for prefix in project.prefixes:
            for item in project.items(prefix):
                # We only care about files directly under the prefix that match the overviews subset
                if isinstance(item, ProjectFile) and project.tracked(item) and item.path in overviews:
                    content = project.read(item.path)
                    if content is not None:
                        candidates[item.path] = content

        knowledge = Knowledge(candidates)

        # Rank the candidates (lexicographically)
        ranking = LexicographicalRanker().rank(knowledge)

        # Remove already loaded files
        already_loaded = coerce_subset(env[KnowledgeEnv].keys())
        ranking = ranking - already_loaded

        if not ranking:
            return

        candidate_knowledge = knowledge & ranking
        formatted = self._knowledge_format.render_chat(candidate_knowledge, ranking)
        builder.add(formatted)
        env[KnowledgeEnv].update(candidate_knowledge)

__all__ = [
    'RootKnowledgeCrammer',
]
