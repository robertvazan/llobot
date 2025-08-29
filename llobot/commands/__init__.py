"""
Command execution framework for roles.

This package defines the `Command` class, which serves as a base for
implementing commands that can be included in a user's request. Roles can
use these commands to manipulate their execution environment.

Submodules
----------

chains
    Command chains.
mentions
    Parser for @command mentions in chat messages.
projects
    Command to select a project.
retrievals
    Command to retrieve a document.
"""
from __future__ import annotations
from llobot.environments import Environment

class Command:
    """
    Base class for commands that can be executed by a role.

    Commands are responsible for parsing a command string and manipulating
    the environment accordingly.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles a command if it is recognized.

        Subclasses should override this method to implement command-specific
        logic. The method should return `True` if the command was handled,
        and `False` otherwise.

        Args:
            text: The unparsed command string.
            env: The environment to manipulate.

        Returns:
            `True` if the command was handled, `False` otherwise.
        """
        return False

    def __call__(self, text: str | list[str], env: Environment):
        """
        Executes the command(s).

        This is a convenience method that calls `handle` and raises an
        exception if the command is not recognized. If a list of commands
        is provided, it will attempt to handle each one.

        Args:
            text: The unparsed command string or a list of them.
            env: The environment to manipulate.

        Raises:
            ValueError: If a command is not handled.
        """
        if isinstance(text, str):
            if not self.handle(text, env):
                raise ValueError(f'Unrecognized: {text}')
        else:
            for t in text:
                self(t, env)

__all__ = [
    'Command',
]
