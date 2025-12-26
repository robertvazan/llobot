"""
Defines the `DummyTool` interface.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.tools import Tool

class DummyTool(Tool):
    """
    Interface for tools that only skip content.
    """

    def skip(self, env: Environment, source: str, at: int) -> int:
        """
        Attempts to locate content to skip starting at the given position.

        It is assumed that `at` is an index pointing to the start of a line.

        Args:
            env: The environment.
            source: The source text.
            at: The index to start looking from.

        Returns:
            The length of the matching content substring, or 0 if no match.
        """
        raise NotImplementedError

__all__ = [
    'DummyTool',
]
