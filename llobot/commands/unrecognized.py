"""
Command for handling unrecognized commands.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.commands import handle_commands

def handle_unrecognized_command(text: str, env: Environment) -> bool:
    """
    Always raises a ValueError, indicating an unrecognized command.

    Args:
        text: The unparsed command string.
        env: The environment.

    Raises:
        ValueError: Always, as this command handles unrecognized commands by failing.
    """
    raise ValueError(f'Unrecognized: {text}')

def handle_unrecognized_commands(env: Environment):
    """
    Handles unrecognized commands by raising an error.
    """
    handle_commands(env, handle_unrecognized_command)

__all__ = [
    'handle_unrecognized_command',
    'handle_unrecognized_commands',
]
