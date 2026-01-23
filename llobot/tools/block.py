"""
Defines the `BlockTool` interface.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.tools import Tool
from llobot.tools.reader import ToolReader

class BlockTool(Tool):
    """
    Interface for tools that parse and execute content blocks.
    """

    def execute(self, env: Environment, reader: ToolReader) -> None:
        """
        Attempts to match and execute a tool call at the current position.

        If a match is found:
        1. Calls `reader.advance()` (or `reader.skip()` for dummy tools) to consume the block.
        2. Parses and executes the tool call logic.
        3. Calls `reader.passed()` if execution succeeds.

        If parsing or execution fails after a match is confirmed (i.e., after calling
        advance/skip), this method raises an exception.

        If no match is found, simply returns without changing the reader state.

        Args:
            env: The execution environment.
            reader: The tool reader providing access to source and position.
        """
        raise NotImplementedError

__all__ = [
    'BlockTool',
]
