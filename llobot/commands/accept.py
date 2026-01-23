"""
Accept command for executing tool calls from model responses.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.prompt import PromptEnv
from llobot.tools.execution import execute_tool_calls

def handle_accept_command(text: str, env: Environment) -> bool:
    """
    Parses and executes tool calls from the last model response.

    This command finds the last model response, parses it for tool calls
    using registered tools, and executes them.

    If no tool calls are found, or if there's no previous response, it's
    considered an error.

    Args:
        text: The command string. Must be "accept".
        env: The environment in which to execute the tool calls.

    Returns:
        `True` if the command was "accept", `False` otherwise.

    Raises:
        ValueError: If there's no response to accept or no tool calls to execute.
    """
    if text != 'accept':
        return False

    prompt_env = env[PromptEnv]
    full_prompt = prompt_env.full

    # Get the last model response from the conversation history.
    last_response = next((m for m in reversed(full_prompt) if m.intent == ChatIntent.RESPONSE), None)
    if not last_response:
        raise ValueError("Nothing to accept.")

    # Execute tool calls.
    count = execute_tool_calls(env, last_response.content)

    if count == 0:
        raise ValueError("No tool calls to execute.")

    prompt_env.swallow()

    return True

def handle_accept_commands(env: Environment):
    """
    Handles `@accept` commands in the environment.

    Args:
        env: The environment to handle commands in.
    """
    handle_commands(env, lambda text, env: handle_accept_command(text, env))

__all__ = [
    'handle_accept_command',
    'handle_accept_commands',
]
