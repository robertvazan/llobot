"""
Command to retrieve documents by wildcard path pattern.
"""
from __future__ import annotations
import re
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge.subsets.parsing import parse_pattern

_WILDCARD_PATH_RE = re.compile(r'^/?(?:[a-zA-Z0-9_.*?-]+/)*[a-zA-Z0-9_.*?-]+$')


class WildcardRetrievalCommand(Command):
    """
    A command that retrieves documents from the knowledge base by a wildcard path pattern.

    The command text is treated as a glob pattern. If it matches one or more
    documents in the knowledge base, those documents are added to the retrievals.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the wildcard retrieval command.

        The command is handled if the text contains a wildcard ('*' or '?') and
        at least one slash ('/'), and it matches at least one document in the
        current project's knowledge.

        Args:
            text: The glob pattern to match.
            env: The environment to manipulate.

        Returns:
            `True` if at least one document was retrieved, `False` otherwise.
        """
        if not _WILDCARD_PATH_RE.fullmatch(text):
            return False

        if ('*' not in text and '?' not in text) or '/' not in text:
            return False

        knowledge_index = env[KnowledgeEnv].index()
        subset = parse_pattern(text)
        matches = list(knowledge_index & subset)

        if matches:
            for match in matches:
                env[RetrievalsEnv].add(match)
            return True

        return False

__all__ = [
    'WildcardRetrievalCommand',
]
