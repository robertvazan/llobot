"""
Commands and steps for document retrieval.

This module provides the `RetrievalStep` for adding retrieved documents to the
context.

Submodules
----------
solo
    Command to retrieve a single document by its path pattern.
"""
from __future__ import annotations
from llobot.commands import Step
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.formats.knowledge import KnowledgeFormat
from llobot.knowledge.indexes import KnowledgeIndex


class RetrievalStep(Step):
    """
    A step that adds retrieved documents to the context if they are not already there.
    """
    _knowledge_format: KnowledgeFormat

    def __init__(self, knowledge_format: KnowledgeFormat):
        """
        Initializes the retrieval step.

        Args:
            knowledge_format: The format to use for rendering retrieved documents.
        """
        self._knowledge_format = knowledge_format

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
                formatted = self._knowledge_format.document_format.render_fresh(path, knowledge[path])
                if formatted:
                    already_present = any(formatted in msg.content for msg in context_messages)
                    if not already_present:
                        paths_to_add.add(path)

        retrieved_knowledge = knowledge & KnowledgeIndex(paths_to_add)
        retrievals_chat = self._knowledge_format.render_fresh(retrieved_knowledge)
        context.add(retrievals_chat)

        retrievals.clear()


__all__ = [
    'RetrievalStep',
]
