"""
Command to retrieve a document by path.
"""
from __future__ import annotations
import re
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge.subsets.parsing import parse_pattern

_PATH_RE = re.compile(r'^(?:~/)?(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+$')

def handle_solo_retrieval_command(text: str, env: Environment) -> bool:
    """
    Retrieves a document from the knowledge base by its path.

    The command text is treated as a path pattern. If it matches a single
    document in the knowledge base, that document is added to the retrievals.
    The pattern can be relative or absolute (starting with '~/'). It cannot
    contain wildcards.

    Args:
        text: The path pattern to match.
        env: The environment to manipulate.

    Returns:
        `True` if a unique document was retrieved, `False` otherwise.
    """
    if not _PATH_RE.fullmatch(text):
        return False

    original_text = text
    if text.startswith('~/'):
        text = '/' + text[2:]

    knowledge_index = env[KnowledgeEnv].index()
    subset = parse_pattern(text)
    matches = list(knowledge_index & subset)

    if len(matches) == 1:
        env[RetrievalsEnv].add(matches[0])
        env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, f"Resolved `{original_text}` to `~/{matches[0]}`."))
        return True

    return False

def handle_solo_retrieval_commands(env: Environment):
    """
    Handles solo retrieval commands in the environment.
    """
    handle_commands(env, handle_solo_retrieval_command)

__all__ = [
    'handle_solo_retrieval_command',
    'handle_solo_retrieval_commands',
]
