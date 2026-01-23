"""
Tool execution logic.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.block import BlockTool
from llobot.tools.reader import ToolReader
from llobot.utils.text import quote_code

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
    reader = ToolReader(source)
    tools = env[ToolEnv].tools
    length = len(source)

    while reader.position < length:
        start_pos = reader.position

        for tool in tools:
            try:
                if isinstance(tool, BlockTool):
                    tool.execute(env, reader)
            except Exception as e:
                # If execution failed (meaning tool matched and advanced/skipped but threw exception)
                if reader.position > start_pos:
                    env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Error executing tool: {quote_code(str(e))}"))
                    # Continue parsing from the new position
                    break
                else:
                    # Tool threw exception without advancing/skipping. Ignore and continue trying other tools.
                    # This shouldn't happen with well-behaved tools, but we handle it.
                    continue

            # If tool executed successfully (moved cursor)
            if reader.position > start_pos:
                break

        # If no tool matched (cursor didn't move), skip to next line
        if reader.position == start_pos:
            try:
                next_newline = source.index('\n', reader.position)
                reader.skip(next_newline + 1 - reader.position)
            except ValueError:
                # Reached end of string
                reader.skip(length - reader.position)

    total_count = reader.tool_count
    success_count = reader.success_count

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
