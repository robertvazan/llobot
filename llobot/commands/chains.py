"""
Command chain implementation for combining multiple commands.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.commands import Command

class CommandChain:
    """
    A class that processes a sequence of commands in order.

    The chain calls `handle_pending` on each of its constituent commands.
    This allows for ordered execution of different command types.
    """
    _commands: tuple[Command, ...]

    def __init__(self, *commands: Command):
        """
        Creates a new command chain.

        Args:
            *commands: A sequence of commands to process in order.
        """
        self._commands = commands

    def handle_pending(self, env: Environment):
        """
        Calls `handle_pending` on each command in the chain.

        Args:
            env: The environment to manipulate.
        """
        for command in self._commands:
            command.handle_pending(env)

__all__ = [
    'CommandChain',
]
