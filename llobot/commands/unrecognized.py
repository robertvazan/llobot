"""
Command for handling unrecognized commands.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.commands import Command

class UnrecognizedCommand(Command):
    """
    A command that raises an error for any command it handles.

    This command is intended to be the last in a command chain to catch
    any commands that were not handled by other commands.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Always raises a ValueError, indicating an unrecognized command.

        Args:
            text: The unparsed command string.
            env: The environment.

        Raises:
            ValueError: Always, as this command handles unrecognized commands by failing.
        """
        raise ValueError(f'Unrecognized: {text}')

__all__ = [
    'UnrecognizedCommand',
]
