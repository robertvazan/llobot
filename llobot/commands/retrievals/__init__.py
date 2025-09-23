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
"""
from __future__ import annotations
from llobot.commands import Step
from llobot.commands.chain import StepChain
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.formats.deltas.knowledge import KnowledgeDeltaFormat
from llobot.knowledge.indexes import KnowledgeIndex


class RetrievalStep(Step):
    """
    A step that adds retrieved documents to the context if they are not already there.
    """
    _knowledge_delta_format: KnowledgeDeltaFormat

    def __init__(self, knowledge_delta_format: KnowledgeDeltaFormat):
        """
        Initializes the retrieval step.

        Args:
            knowledge_delta_format: The format to use for rendering retrieved documents.
        """
        self._knowledge_delta_format = knowledge_delta_format

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
        context_messages = context.messages
        paths_to_add = set()
        for path in retrieved_paths:
            if path in knowledge:
                formatted = self._knowledge_delta_format.document_delta_format.render_fresh(path, knowledge[path])
                if formatted:
                    already_present = any(formatted in msg.content for msg in context_messages)
                    if not already_present:
                        paths_to_add.add(path)

        retrieved_knowledge = knowledge & KnowledgeIndex(paths_to_add)
        retrievals_chat = self._knowledge_delta_format.render_fresh_chat(retrieved_knowledge)
        context.add(retrievals_chat)

        retrievals.clear()


def standard_retrieval_commands() -> StepChain:
    """
    Returns a step chain with standard retrieval commands.

    This includes exact and wildcard retrieval.
    """
    from llobot.commands.retrievals.exact import ExactRetrievalCommand
    from llobot.commands.retrievals.wildcard import WildcardRetrievalCommand
    return StepChain(
        ExactRetrievalCommand(),
        WildcardRetrievalCommand(),
    )


__all__ = [
    'RetrievalStep',
    'standard_retrieval_commands',
]
