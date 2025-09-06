"""
Command queue environment component.
"""
from __future__ import annotations
from typing import Iterable

class CommandQueueEnv:
    """
    An environment component that holds a set of unprocessed command strings.
    """
    _commands: set[str]

    def __init__(self):
        self._commands = set()

    def add(self, commands: str | Iterable[str]):
        """
        Adds one or more commands to the queue.

        Args:
            commands: A single command string or an iterable of command strings.
        """
        if isinstance(commands, str):
            self._commands.add(commands)
        else:
            self._commands.update(commands)

    def get(self) -> list[str]:
        """
        Gets the list of unprocessed commands, sorted for consistency.

        Returns:
            A sorted list of command strings.
        """
        return sorted(list(self._commands))

    def consume(self, command: str):
        """
        Removes a command from the queue.

        Args:
            command: The command string to remove.
        """
        self._commands.discard(command)

__all__ = [
    'CommandQueueEnv',
]
