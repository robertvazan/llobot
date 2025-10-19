"""
Commands and steps for document retrieval.

This module provides functions for adding retrieved documents to the
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
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.formats.deltas.knowledge import KnowledgeDeltaFormat, standard_knowledge_delta_format
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking.rankers import KnowledgeRanker, standard_ranker
from llobot.commands.retrievals.exact import handle_exact_retrieval_commands
from llobot.commands.retrievals.overviews import assume_overview_retrieval_commands
from llobot.commands.retrievals.wildcard import handle_wildcard_retrieval_commands


def flush_retrieval_commands(
    env: Environment,
    *,
    knowledge_delta_format: KnowledgeDeltaFormat | None = None,
    ranker: KnowledgeRanker | None = None,
):
    """
    Adds retrieved documents to the context if they are not already there.

    The documents are added in an order determined by the provided ranker.

    Args:
        env: The current environment.
        knowledge_delta_format: The format to use for rendering retrieved documents.
                                Defaults to the standard format.
        ranker: The ranker to use for ordering retrieved documents.
                Defaults to the standard ranker.
    """
    if knowledge_delta_format is None:
        knowledge_delta_format = standard_knowledge_delta_format()
    if ranker is None:
        ranker = standard_ranker()

    retrievals = env[RetrievalsEnv]
    retrieved_paths = retrievals.get()
    knowledge = env[KnowledgeEnv].get()
    context = env[ContextEnv]

    # Check what is already in context to avoid duplicates.
    context_branch = context.build()
    paths_to_add = set()
    for path in retrieved_paths:
        if path in knowledge:
            formatted = knowledge_delta_format.document_delta_format.render_fresh(path, knowledge[path])
            if formatted:
                already_present = any(formatted in msg.content for msg in context_branch)
                if not already_present:
                    paths_to_add.add(path)

    retrieved_knowledge = knowledge & KnowledgeIndex(paths_to_add)
    ranking = ranker.rank(retrieved_knowledge)
    retrievals_chat = knowledge_delta_format.render_fresh_chat(retrieved_knowledge, ranking=ranking)
    context.add(retrievals_chat)

    retrievals.clear()


def handle_retrieval_commands(env: Environment):
    """
    Handles all retrieval commands and adds retrieved documents to the context.

    This includes exact and wildcard retrieval commands, followed by a step to
    add ancestor overviews, and finally the step that adds all retrieved
    documents to the context.

    Args:
        env: The environment to manipulate.
    """
    handle_exact_retrieval_commands(env)
    handle_wildcard_retrieval_commands(env)
    assume_overview_retrieval_commands(env)
    flush_retrieval_commands(env)


__all__ = [
    'flush_retrieval_commands',
    'handle_retrieval_commands',
]
