"""
Command to select a project.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv

def handle_project_command(text: str, env: Environment) -> bool:
    """
    Handles the project selection command.

    If `text` is a key that matches one or more projects in the library,
    those projects are added to the environment's `ProjectEnv`.

    Args:
        text: The command string, used as a key for project lookup.
        env: The environment to manipulate.

    Returns:
        `True` if any project was selected, `False` otherwise.
    """
    project_env = env[ProjectEnv]
    found = project_env.add(text)
    return bool(found)

def handle_project_commands(env: Environment):
    """
    Handles project selection commands (e.g. `@myproject`) in the environment.
    """
    project_env = env[ProjectEnv]
    before = project_env.union.summary
    handle_commands(env, handle_project_command)
    after = project_env.union.summary

    if before != after:
        if after:
            text = "Projects:\n\n" + "\n".join(f"- {item}" for item in after)
            env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, text))

__all__ = [
    'handle_project_command',
    'handle_project_commands',
]
