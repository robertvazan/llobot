"""
Command chain implementation for combining multiple commands.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.commands import Command

class CommandChain(Command):
    """
    A command that tries a sequence of other commands in order.

    The chain handles a command if any of its constituent commands handle it.
    The first command to handle the command stops the processing.
    """
    _commands: tuple[Command, ...]

    def __init__(self, *commands: Command):
        """
        Creates a new command chain.

        Args:
            *commands: A sequence of commands to try in order.
        """
        self._commands = commands

    def handle(self, text: str, env: Environment) -> bool:
        """
        Tries to handle the command with each command in the chain.

        Args:
            text: The unparsed command string.
            env: The environment to manipulate.

        Returns:
            `True` if any command in the chain handled the command, `False` otherwise.
        """
        for command in self._commands:
            if command.handle(text, env):
                return True
        return False

__all__ = [
    'CommandChain',
]
