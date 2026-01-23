"""
Tool execution logic.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.tools.parsing import parse_tool_calls

def execute_tool_calls(env: Environment, source: str) -> int:
    """
    Parses and executes tool calls from a source string.

    Tool calls are parsed and executed in an interleaved manner, so that
    subsequent tool calls see the effects of previous ones.

    If any tool calls were executed, a summary status message is added to the
    environment's context.

    Args:
        env: The environment to execute in.
        source: The source string containing tool calls.

    Returns:
        The number of tool calls found and processed.
    """
    total_count = 0
    success_count = 0

    for call in parse_tool_calls(env, source):
        total_count += 1
        if call.try_execute(env):
            success_count += 1

    if total_count > 0:
        context_env = env[ContextEnv]
        if success_count == total_count:
            summary_line = f"✅ All {total_count} tool calls executed."
        else:
            summary_line = f"❌ {success_count} of {total_count} tool calls executed."
        context_env.add(ChatMessage(ChatIntent.STATUS, summary_line))

    return total_count

__all__ = [
    'execute_tool_calls',
]
