"""
Command to select a model.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.model import ModelEnv

def handle_model_command(text: str, env: Environment) -> bool:
    """
    Handles the model selection command.

    If `text` is a key that matches a model in the library,
    that model is selected in the environment's `ModelEnv`.

    Args:
        text: The command string, used as a key for model lookup.
        env: The environment to manipulate.

    Returns:
        `True` if a model was selected, `False` otherwise.
    """
    model_env = env[ModelEnv]
    found = model_env.select(text)
    return bool(found)

def handle_model_commands(env: Environment):
    """
    Handles `@model` commands in the environment.
    """
    model_env = env[ModelEnv]
    try:
        before = model_env.get()
    except ValueError:
        before = None

    handle_commands(env, handle_model_command)

    try:
        after = model_env.get()
    except ValueError:
        after = None

    if before != after and after:
        text = f"Selected LLM: `{after.identifier}`"
        env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, text))

__all__ = [
    'handle_model_command',
    'handle_model_commands',
]
