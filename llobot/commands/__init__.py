"""
Command and step execution framework for roles.

This package defines functions for handling user commands extracted from prompts.

Submodules
----------

project
    Command to select a project.
knowledge
    Function to load project knowledge.
retrievals
    Commands and functions for document retrieval.
session
    Commands and functions to manage session state.
unrecognized
    Command to handle unrecognized commands.
approve
    Command to save an example.
"""
from __future__ import annotations
from typing import Callable
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv

def handle_commands(env: Environment, handler: Callable[[str, Environment], bool]):
    """
    Handles all pending commands in the queue that the handler recognizes.

    It iterates through all commands in `CommandsEnv`, calls `handler` on
    each, and if `handler` returns `True`, the command is consumed from
    the queue.

    Args:
        env: The environment to manipulate.
        handler: The function to handle a command. It should return `True` if
                 the command was handled, and `False` otherwise.
    """
    queue = env[CommandsEnv]
    for command in queue.get():
        if handler(command, env):
            queue.consume(command)

__all__ = [
    'handle_commands',
]
