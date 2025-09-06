"""
Command execution framework for roles.

This package defines the `Command` class, which serves as a base for
implementing commands that can be included in a user's request. Roles can
use these commands to manipulate their execution environment.

Submodules
----------

chains
    Command chains.
projects
    Command to select a project.
knowledge
    Command to load project knowledge.
retrievals
    Command to retrieve a document.
cutoffs
    Command to set knowledge cutoff.
unrecognized
    Command to handle unrecognized commands.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.environments.command_queue import CommandQueueEnv

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

    def process(self, env: Environment):
        """
        Perform processing after all commands of this type have been handled.

        This method is called once by `handle_pending` after attempting to
        handle all commands in the queue. Subclasses can override it to
        perform actions that depend on the complete set of handled commands.

        Args:
            env: The environment.
        """
        pass

    def handle_pending(self, env: Environment):
        """
        Handles all pending commands in the queue that this command recognizes.

        It iterates through all commands in `CommandQueueEnv`, calls `handle()` on
        each, and if `handle()` returns `True`, the command is consumed from
        the queue. After checking all commands, `process()` is called.

        Args:
            env: The environment to manipulate.
        """
        queue = env[CommandQueueEnv]
        for command in queue.get():
            if self.handle(command, env):
                queue.consume(command)
        self.process(env)

__all__ = [
    'Command',
]
