"""
Command to echo the prompt context.
"""
from __future__ import annotations
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.prompt import PromptEnv
from llobot.formats.monolithic import standard_monolithic_format
from llobot.formats.monolithic.details import DetailsMonolithicFormat
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent

def handle_echo_command(text: str, env: Environment) -> bool:
    """
    Handles the echo command.

    If the command is `@echo` or `@echo-details`, it renders the current context
    using a monolithic format and adds it as a status message to the context.
    It also swallows the prompt to prevent the model from generating a response.

    Args:
        text: The command string.
        env: The environment to manipulate.

    Returns:
        `True` if the command was executed, `False` otherwise.
    """
    if text == 'echo':
        format = standard_monolithic_format()
    elif text == 'echo-details':
        format = DetailsMonolithicFormat()
    else:
        return False

    context = env[ContextEnv].build()
    content = format.render(context)

    if content:
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, content))

    env[PromptEnv].swallow()
    return True

def handle_echo_commands(env: Environment):
    """
    Handles `@echo` commands in the environment.
    """
    handle_commands(env, handle_echo_command)

__all__ = [
    'handle_echo_command',
    'handle_echo_commands',
]
