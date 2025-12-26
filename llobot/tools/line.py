"""
Defines the `LineTool` interface.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.tools import Tool, ToolCall

class LineTool(Tool):
    """
    Interface for tools that parse single lines within a tool script.
    """

    def matches_line(self, env: Environment, line: str) -> bool:
        """
        Checks if the line matches this tool's command format.

        Exceptions raised by this method are treated as a failure to match.

        Args:
            env: The environment.
            line: The command line to check.

        Returns:
            True if it matches.
        """
        raise NotImplementedError

    def parse_line(self, env: Environment, line: str) -> ToolCall:
        """
        Parses a single line into a ToolCall.

        Args:
            env: The environment.
            line: The command line to parse.

        Returns:
            A ToolCall instance.
        """
        raise NotImplementedError

__all__ = [
    'LineTool',
]
