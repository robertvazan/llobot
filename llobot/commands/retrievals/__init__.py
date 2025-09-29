"""
Commands and steps for document retrieval.

This module provides the `RetrievalStep` for adding retrieved documents to the
context.

Submodules
----------
exact
    Command to retrieve one or more documents by an exact path pattern.
solo
    Command to retrieve a single document by its path pattern.
wildcard
    Command to retrieve documents using wildcard patterns.
overviews
    Step to retrieve overview documents for existing retrievals.
"""
from __future__ import annotations
from llobot.commands import Step
from llobot.commands.chain import StepChain
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.formats.deltas.knowledge import KnowledgeDeltaFormat, standard_knowledge_delta_format
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking.rankers import KnowledgeRanker, standard_ranker


class RetrievalStep(Step):
    """
    A step that adds retrieved documents to the context if they are not already there.

    The documents are added in an order determined by the provided ranker.
    """
    _knowledge_delta_format: KnowledgeDeltaFormat
    _ranker: KnowledgeRanker

    def __init__(
        self,
        knowledge_delta_format: KnowledgeDeltaFormat | None = None,
        ranker: KnowledgeRanker | None = None,
    ):
        """
        Initializes the retrieval step.

        Args:
            knowledge_delta_format: The format to use for rendering retrieved documents.
                                    Defaults to the standard format.
            ranker: The ranker to use for ordering retrieved documents.
                    Defaults to the standard ranker.
        """
        if knowledge_delta_format is None:
            knowledge_delta_format = standard_knowledge_delta_format()
        self._knowledge_delta_format = knowledge_delta_format
        if ranker is None:
            ranker = standard_ranker()
        self._ranker = ranker

    def process(self, env: Environment):
        """
        Processes retrievals, adding new documents to the context.

        Args:
            env: The current environment.
        """
        retrievals = env[RetrievalsEnv]
        retrieved_paths = retrievals.get()
        knowledge = env[KnowledgeEnv].get()
        context = env[ContextEnv]

        # Check what is already in context to avoid duplicates.
        context_branch = context.build()
        paths_to_add = set()
        for path in retrieved_paths:
            if path in knowledge:
                formatted = self._knowledge_delta_format.document_delta_format.render_fresh(path, knowledge[path])
                if formatted:
                    already_present = any(formatted in msg.content for msg in context_branch)
                    if not already_present:
                        paths_to_add.add(path)

        retrieved_knowledge = knowledge & KnowledgeIndex(paths_to_add)
        ranking = self._ranker.rank(retrieved_knowledge)
        retrievals_chat = self._knowledge_delta_format.render_fresh_chat(retrieved_knowledge, ranking=ranking)
        context.add(retrievals_chat)

        retrievals.clear()


def standard_retrieval_step() -> StepChain:
    """
    Returns a step chain with standard retrieval commands and the retrieval step.

    This includes exact and wildcard retrieval commands, followed by a step to
    add ancestor overviews, and finally the step that adds all retrieved
    documents to the context.
    """
    from llobot.commands.retrievals.exact import ExactRetrievalCommand
    from llobot.commands.retrievals.overviews import OverviewRetrievalStep
    from llobot.commands.retrievals.wildcard import WildcardRetrievalCommand
    return StepChain(
        ExactRetrievalCommand(),
        WildcardRetrievalCommand(),
        OverviewRetrievalStep(),
        RetrievalStep(),
    )


__all__ = [
    'RetrievalStep',
    'standard_retrieval_step',
]
