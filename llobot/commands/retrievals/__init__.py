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
from llobot.environments.projects import ProjectEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.environments.seen import SeenEnv
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking.rankers import KnowledgeRanker, standard_ranker
from llobot.commands.retrievals.exact import handle_exact_retrieval_commands
from llobot.commands.retrievals.overviews import assume_overview_retrieval_commands
from llobot.commands.retrievals.wildcard import handle_wildcard_retrieval_commands


def flush_retrieval_commands(
    env: Environment,
    *,
    knowledge_format: KnowledgeFormat | None = None,
    ranker: KnowledgeRanker | None = None,
):
    """
    Adds retrieved documents to the context if they are not already there.

    The documents are added in an order determined by the provided ranker.

    Args:
        env: The current environment.
        knowledge_format: The format to use for rendering retrieved documents.
                                Defaults to the standard format.
        ranker: The ranker to use for ordering retrieved documents.
                Defaults to the standard ranker.
    """
    if knowledge_format is None:
        knowledge_format = standard_knowledge_format()
    if ranker is None:
        ranker = standard_ranker()

    retrievals = env[RetrievalsEnv]
    retrieved_paths = retrievals.get()
    project = env[ProjectEnv].union
    seen_env = env[SeenEnv]
    context = env[ContextEnv]

    docs = {}

    # We iterate over all retrieved paths. Read operation will return None
    # for files that are unreadable or do not exist, effectively filtering them out.
    for path in retrieved_paths:
        content = project.read(path)
        if content is not None:
            # We skip files that have already been seen in the context.
            # Document format guarantees non-empty output, so we don't need to check it.
            if path not in seen_env:
                docs[path] = content

    retrieved_knowledge = Knowledge(docs)
    seen_env.update(retrieved_knowledge)

    ranking = ranker.rank(retrieved_knowledge)
    retrievals_chat = knowledge_format.render_chat(retrieved_knowledge, ranking=ranking)
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
