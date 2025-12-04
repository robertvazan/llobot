"""
Accept command for executing tool calls from model responses.
"""
from __future__ import annotations
from typing import Iterable
from llobot.chats.intent import ChatIntent
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.prompt import PromptEnv
from llobot.environments.status import StatusEnv
from llobot.environments.tools import ToolEnv
from llobot.tools import Tool
from llobot.tools.parsing import parse_tool_calls
from llobot.utils.text import markdown_code_details

def handle_accept_command(text: str, env: Environment, tools: Iterable[Tool]) -> bool:
    """
    Parses and executes tool calls from the last model response.

    This command finds the last model response, parses it for tool calls
    (e.g., file edits, removals), and executes them. The results of each
    execution are reported in the `StatusEnv`.

    If no tool calls are found, or if there's no previous response, it's
    considered an error.

    Args:
        text: The command string. Must be "accept".
        env: The environment in which to execute the tool calls.
        tools: Iterable of Tool implementations used to parse tool calls.

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

    response_content = last_response.content

    # Parse tool calls from the last response using provided tools.
    tool_calls = list(parse_tool_calls(response_content, tools))

    if not tool_calls:
        raise ValueError("No tool calls to execute.")

    status_env = env[StatusEnv]
    tool_env = env[ToolEnv]
    success_count = 0

    for call in tool_calls:
        success = call.try_execute(env)
        if success:
            success_count += 1

        log_content = tool_env.flush_log()
        summary = f"{'Success' if success else 'Failure'}: {call.title}"

        # Output a details/summary section with an untyped code block (no language).
        details = markdown_code_details(summary, '', log_content)
        status_env.append(details)

    total_count = len(tool_calls)
    if success_count == total_count:
        summary_line = f"✅ All {total_count} tool calls executed."
    else:
        summary_line = f"❌ {success_count} of {total_count} tool calls executed."

    status_env.append(summary_line)

    return True

def handle_accept_commands(env: Environment, tools: Iterable[Tool]):
    """
    Handles `@accept` commands in the environment.

    Args:
        env: The environment to handle commands in.
        tools: Iterable of Tool implementations used to parse tool calls.
    """
    handle_commands(env, lambda text, env: handle_accept_command(text, env, tools))

__all__ = [
    'handle_accept_command',
    'handle_accept_commands',
]
