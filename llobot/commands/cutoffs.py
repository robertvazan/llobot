"""
Command to set knowledge cutoff.
"""
from __future__ import annotations
import llobot.time
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv

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
        cutoff = llobot.time.try_parse(text)
        if cutoff:
            env[CutoffEnv].set(cutoff)
            return True
        return False

__all__ = [
    'CutoffCommand',
]
