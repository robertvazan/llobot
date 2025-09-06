"""
Command and step execution framework for roles.

This package defines `Step` and `Command` classes. Steps are processed
sequentially. Commands are a type of step that is driven by user commands
extracted from prompts.

Submodules
----------

chains
    Step chains.
projects
    Command to select a project.
knowledge
    Step to load project knowledge.
retrievals
    Commands and steps for document retrieval.
cutoffs
    Command and step to set knowledge cutoff.
unrecognized
    Command to handle unrecognized commands.
custom
    Step for executing arbitrary callables.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.environments.command_queue import CommandQueueEnv

class Step:
    """
    Base class for processing steps in a role's command chain.
    """
    def process(self, env: Environment):
        """
        Executes the step. Subclasses should override this method.

        Args:
            env: The environment to manipulate.
        """
        pass

class Command(Step):
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
        Handles all pending commands in the queue that this command recognizes.

        It iterates through all commands in `CommandQueueEnv`, calls `handle()` on
        each, and if `handle()` returns `True`, the command is consumed from
        the queue.

        Args:
            env: The environment to manipulate.
        """
        queue = env[CommandQueueEnv]
        for command in queue.get():
            if self.handle(command, env):
                queue.consume(command)

__all__ = [
    'Step',
    'Command',
]
