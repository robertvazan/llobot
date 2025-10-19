"""
Command to retrieve documents by wildcard path pattern.
"""
from __future__ import annotations
import re
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge.subsets.parsing import parse_pattern

_WILDCARD_PATH_RE = re.compile(r'^/?(?:[a-zA-Z0-9_.*?-]+/)*[a-zA-Z0-9_.*?-]+$')


def handle_wildcard_retrieval_command(text: str, env: Environment) -> bool:
    """
    Retrieves documents from the knowledge base by a wildcard path pattern.

    The command text is treated as a glob pattern. If it matches one or more
    documents in the knowledge base, those documents are added to the retrievals.

    Args:
        text: The glob pattern to match.
        env: The environment to manipulate.

    Returns:
        `True` if at least one document was retrieved, `False` otherwise.
    """
    if not _WILDCARD_PATH_RE.fullmatch(text):
        return False

    if '*' not in text and '?' not in text:
        return False

    knowledge_index = env[KnowledgeEnv].index()
    subset = parse_pattern(text)
    matches = list(knowledge_index & subset)

    if matches:
        for match in matches:
            env[RetrievalsEnv].add(match)
        return True

    return False

def handle_wildcard_retrieval_commands(env: Environment):
    """
    Handles wildcard retrieval commands in the environment.
    """
    handle_commands(env, handle_wildcard_retrieval_command)

__all__ = [
    'handle_wildcard_retrieval_command',
    'handle_wildcard_retrieval_commands',
]
