"""
Tool call parsing logic.
"""
from __future__ import annotations
from typing import Iterator
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import ToolCall
from llobot.tools.block import BlockTool
from llobot.tools.dummy import DummyTool

def parse_tool_calls(env: Environment, source: str) -> Iterator[ToolCall]:
    """
    Parses tool calls from a source string using registered tools.

    It scans the source string line by line. At each line, it attempts to match
    against the registered tools in order. If a match is found, the tool call is
    parsed and yielded (if not `None`), and scanning advances past the matched
    text. If the match does not consume the entire line, the rest of the line is
    skipped. If no match is found on a line, the parser skips to the next line.

    Args:
        env: The environment containing registered tools.
        source: The text containing tool calls.

    Yields:
        Parsed `ToolCall` objects. `InvalidToolCall` is yielded for parse errors.
    """
    at = 0
    length = len(source)
    tools = env[ToolEnv].tools

    while at < length:
        matched_len = 0
        matched_tool = None

        for tool in tools:
            try:
                if isinstance(tool, BlockTool):
                    l = tool.slice(env, source, at)
                elif isinstance(tool, DummyTool):
                    l = tool.skip(env, source, at)
                else:
                    l = 0

                if l > 0:
                    matched_len = l
                    matched_tool = tool
                    break
            except Exception:
                continue

        if matched_tool:
            if isinstance(matched_tool, BlockTool):
                snippet = source[at:at+matched_len]
                for call in matched_tool.try_parse(env, snippet):
                    yield call
            at += matched_len

        # If the match didn't consume a full line, skip to the next one.
        # If no tool matched, skip the current line.
        if not matched_tool or at < length and source[at - 1] != '\n':
            try:
                next_newline = source.index('\n', at)
                at = next_newline + 1
            except ValueError:
                at = length # Reached end of string

__all__ = [
    'parse_tool_calls',
]
