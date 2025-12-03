"""
Tool call parsing logic.
"""
from __future__ import annotations
from typing import Iterable, Iterator
from llobot.tools import Tool, ToolCall

def parse_tool_calls(source: str, tools: Iterable[Tool]) -> Iterator[ToolCall]:
    """
    Parses tool calls from a source string using a list of tools.

    It scans the source string line by line. At each line, it attempts to match
    against the provided tools in order. If a match is found, the tool call is
    parsed and yielded (if not `None`), and scanning advances past the matched
    text. If the match does not consume the entire line, the rest of the line is
    skipped. If no match is found on a line, the parser skips to the next line.

    Args:
        source: The text containing tool calls.
        tools: The list of tools to attempt matching.

    Yields:
        Parsed `ToolCall` objects. `InvalidToolCall` is yielded for parse errors.
    """
    at = 0
    length = len(source)
    tool_list = list(tools)

    while at < length:
        matched_len = 0
        matched_tool = None

        for tool in tool_list:
            try:
                l = tool.slice(source, at)
                if l > 0:
                    matched_len = l
                    matched_tool = tool
                    break
            except Exception:
                continue

        if matched_tool:
            snippet = source[at:at+matched_len]
            call = matched_tool.try_parse(snippet)
            if call is not None:
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
