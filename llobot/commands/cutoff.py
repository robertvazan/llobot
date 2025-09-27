"""
Command and step to set knowledge cutoff.
"""
from __future__ import annotations
from llobot.commands import Command, Step
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.session import SessionEnv
from llobot.knowledge.archives import KnowledgeArchive
from llobot.utils.time import current_time, format_time, try_parse_time

class CutoffCommand(Command):
    """
    A command to set the knowledge cutoff from a timestamp string.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the command if the text is a valid timestamp.

        Args:
            text: The unparsed command string, expected to be a timestamp.
            env: The environment to manipulate.

        Returns:
            `True` if the command was handled, `False` otherwise.
        """
        cutoff = try_parse_time(text)
        if cutoff:
            env[CutoffEnv].set(cutoff)
            return True
        return False

class ImplicitCutoffStep(Step):
    """
    A step that sets the knowledge cutoff to the current time if it's not
    already set.
    """
    _archive: KnowledgeArchive | None

    def __init__(self, archive: KnowledgeArchive | None = None):
        """
        Initializes the step.

        Args:
            archive: The knowledge archive to refresh, if any.
        """
        self._archive = archive

    def process(self, env: Environment):
        """
        If no cutoff is set and this is the last prompt, this method refreshes
        all current projects (if an archive is provided), sets the cutoff to
        the current time, and adds a session message.

        Args:
            env: The environment.
        """
        if env[PromptEnv].is_last and env[CutoffEnv].get() is None:
            if self._archive:
                env[ProjectEnv].union.refresh(self._archive)
            cutoff = current_time()
            env[CutoffEnv].set(cutoff)
            env[SessionEnv].append(f"Data cutoff: @{format_time(cutoff)}")

__all__ = [
    'CutoffCommand',
    'ImplicitCutoffStep',
]
