"""
Accept command for executing tool calls from model responses.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.parsing import parse_tool_calls
from llobot.utils.text import markdown_code_details

def handle_accept_command(text: str, env: Environment) -> bool:
    """
    Parses and executes tool calls from the last model response.

    This command finds the last model response, parses it for tool calls
    using registered tools, and executes them. Execution logs are reported
    in the `ContextEnv` as status messages, while tool outputs are appended
    to the `ContextEnv` as system messages.

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

    response_content = last_response.content

    # Parse tool calls from the last response using registered tools.
    tool_calls = list(parse_tool_calls(env, response_content))

    if not tool_calls:
        raise ValueError("No tool calls to execute.")

    tool_env = env[ToolEnv]
    context_env = env[ContextEnv]
    success_count = 0

    for i, call in enumerate(tool_calls):
        if i > 0:
            tool_env.log("")

        tool_env.log(f"Running tool: {call.title}")
        success = call.try_execute(env)
        tool_env.log("Success." if success else "Failed.")

        if success:
            success_count += 1

        output_content = tool_env.flush_output()
        if output_content:
            context_env.add(ChatMessage(ChatIntent.SYSTEM, output_content))

    # Output log details
    log_content = tool_env.flush_log()
    if log_content:
        details = markdown_code_details("Tool call log", '', log_content)
        context_env.add(ChatMessage(ChatIntent.STATUS, details))

    total_count = len(tool_calls)
    if success_count == total_count:
        summary_line = f"✅ All {total_count} tool calls executed."
    else:
        summary_line = f"❌ {success_count} of {total_count} tool calls executed."

    context_env.add(ChatMessage(ChatIntent.STATUS, summary_line))

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
