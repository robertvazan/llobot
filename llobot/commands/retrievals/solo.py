"""
Command to retrieve a document by path.
"""
from __future__ import annotations
import re
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge.subsets import match_glob

_PATH_RE = re.compile(r'^/?(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+$')

class SoloRetrievalCommand(Command):
    """
    A command that retrieves a document from the knowledge base by its path.

    The command text is treated as a path pattern. If it matches a single
    document in the knowledge base, that document is added to the retrievals.
    The pattern can be relative or absolute (starting with '/'). It cannot
    contain wildcards.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the retrieval command.

        The command is handled if the text looks like a path and matches
        exactly one document in the current project's knowledge.

        Args:
            text: The path pattern to match.
            env: The environment to manipulate.

        Returns:
            `True` if a unique document was retrieved, `False` otherwise.
        """
        if not _PATH_RE.fullmatch(text) or ('.' not in text and '/' not in text):
            return False

        knowledge_index = env[KnowledgeEnv].index()
        subset = match_glob(text)
        matches = list(knowledge_index & subset)

        if len(matches) == 1:
            env[RetrievalsEnv].add(matches[0])
            return True

        return False

__all__ = [
    'SoloRetrievalCommand',
]
