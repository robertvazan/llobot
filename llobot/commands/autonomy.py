"""
Command to select an autonomy profile.
"""
from __future__ import annotations
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.autonomy import AutonomyEnv

def handle_autonomy_command(text: str, env: Environment) -> bool:
    """
    Handles the autonomy selection command.

    If `text` is in the format `autonomy:<profile>`, it attempts to select
    the specified autonomy profile.

    Args:
        text: The command string.
        env: The environment to manipulate.

    Returns:
        `True` if an autonomy profile was selected, `False` otherwise.
    """
    if not text.startswith('autonomy:'):
        return False

    profile_name = text[len('autonomy:'):]
    autonomy_env = env[AutonomyEnv]
    found = autonomy_env.select(profile_name)
    return bool(found)

def handle_autonomy_commands(env: Environment):
    """
    Handles `@autonomy:<profile>` commands in the environment.
    """
    handle_commands(env, handle_autonomy_command)

__all__ = [
    'handle_autonomy_command',
    'handle_autonomy_commands',
]
