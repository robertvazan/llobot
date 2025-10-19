"""
Commands and functions to manage session state.
"""
from __future__ import annotations
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.session import SessionEnv
from llobot.utils.time import current_time, format_time, try_parse_time

def handle_session_command(text: str, env: Environment) -> bool:
    """
    A command to set the session ID from a timestamp string.

    Args:
        text: The unparsed command string, expected to be a timestamp.
        env: The environment to manipulate.

    Returns:
        `True` if the command was handled, `False` otherwise.
    """
    session_id = try_parse_time(text)
    if session_id:
        env[SessionEnv].set_id(session_id)
        return True
    return False

def handle_session_commands(env: Environment):
    """
    Handles session ID commands in the environment.
    """
    handle_commands(env, handle_session_command)

def ensure_session_command(env: Environment):
    """
    Sets the session ID to the current time if it's not
    already set, and adds a session message with the ID.

    Args:
        env: The environment.
    """
    session_env = env[SessionEnv]
    if session_env.get_id() is None:
        session_id = current_time()
        session_env.set_id(session_id)
        session_env.append(f"Session: @{format_time(session_id)}")

__all__ = [
    'handle_session_command',
    'handle_session_commands',
    'ensure_session_command',
]
