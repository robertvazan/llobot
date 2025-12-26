"""
Defines the `BlockTool` interface.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.tools import Tool, ToolCall, InvalidToolCall

class BlockTool(Tool):
    """
    Interface for tools that parse content blocks into tool calls.
    """

    def slice(self, env: Environment, source: str, at: int) -> int:
        """
        Attempts to locate a tool call starting at the given position.

        It is assumed that `at` is an index pointing to the start of a line.

        Args:
            env: The environment.
            source: The source text.
            at: The index to start looking from.

        Returns:
            The length of the matching tool call substring, or 0 if no match.
            The returned slice does not need to include a trailing newline.
        """
        raise NotImplementedError

    def parse(self, env: Environment, source: str) -> ToolCall | None:
        """
        Parses a source string into a `ToolCall`.

        This method is only called with a `source` string that has been
        successfully matched by `slice()`.

        Args:
            env: The environment.
            source: The string identified by `slice`.

        Returns:
            A `ToolCall` instance, or `None` to indicate that this tool call
            should be silently skipped.
        """
        raise NotImplementedError

    def try_parse(self, env: Environment, source: str) -> ToolCall | None:
        """
        Attempts to parse a source string, returning an invalid call on failure.

        Args:
            env: The environment.
            source: The string identified by `slice`.

        Returns:
            A `ToolCall`, `InvalidToolCall`, or `None`.
        """
        try:
            return self.parse(env, source)
        except Exception as e:
            return InvalidToolCall(e)

__all__ = [
    'BlockTool',
]
