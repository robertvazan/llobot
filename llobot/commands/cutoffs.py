"""
Command and step to set knowledge cutoff.
"""
from __future__ import annotations
from llobot.time import try_parse_time, current_time, format_time
from llobot.commands import Command, Step
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.session_messages import SessionMessageEnv
from llobot.knowledge.archives import KnowledgeArchive

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
        If no cutoff is set and recording is active, this method refreshes the
        current project (if an archive is provided), sets the cutoff to the
        current time, and adds a session message.

        Args:
            env: The environment.
        """
        if env[ReplayEnv].recording() and env[CutoffEnv].get() is None:
            project = env[ProjectEnv].get()
            if project and self._archive:
                knowledge = project.load()
                self._archive.refresh(project.name, knowledge)
            cutoff = current_time()
            env[CutoffEnv].set(cutoff)
            env[SessionMessageEnv].append(f"Cutoff: @{format_time(cutoff)}")

__all__ = [
    'CutoffCommand',
    'ImplicitCutoffStep',
]
