"""
Command to retrieve documents by an exact path pattern.
"""
from __future__ import annotations
import re
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge.subsets.parsing import parse_pattern

_PATH_RE = re.compile(r'^/?(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+$')

def handle_exact_retrieval_command(text: str, env: Environment) -> bool:
    """
    Retrieves documents from the knowledge base by their path.

    The command text is treated as a path pattern. If it matches one or more
    documents in the knowledge base, those documents are added to the retrievals.
    The pattern can be relative or absolute (starting with '/'). It cannot
    contain wildcards.

    Args:
        text: The path pattern to match.
        env: The environment to manipulate.

    Returns:
        `True` if at least one document was retrieved, `False` otherwise.
    """
    if not _PATH_RE.fullmatch(text):
        return False

    knowledge_index = env[KnowledgeEnv].index()
    subset = parse_pattern(text)
    matches = list(knowledge_index & subset)

    if matches:
        for match in matches:
            env[RetrievalsEnv].add(match)
        return True

    return False

def handle_exact_retrieval_commands(env: Environment):
    """
    Handles exact retrieval commands in the environment.
    """
    handle_commands(env, handle_exact_retrieval_command)

__all__ = [
    'handle_exact_retrieval_command',
    'handle_exact_retrieval_commands',
]
