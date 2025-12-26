"""
Tools for llobot.

This package provides the `Tool` and `ToolCall` interfaces. Implementations
for various tools are available in submodules.

Submodules
----------
block
    Base class for tools that parse content blocks.
dummy
    Base class for tools that skip content.
code
    A tool for skipping code blocks.
fenced
    A base class for tools that use fenced code blocks.
files
    A tool for creating or updating files from file listings.
move
    A tool for moving files.
parsing
    A function to parse tool calls from text.
remove
    A tool for removing files.
"""
from __future__ import annotations
from functools import cache
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.utils.values import ValueTypeMixin

class ToolCall(ValueTypeMixin):
    """
    Represents a parsed tool call ready for execution.
    """

    @property
    def title(self) -> str:
        """
        Returns a summary or header of the tool call.

        Example: "rm path/to/file" or "file path/to/file".
        """
        raise NotImplementedError

    def execute(self, env: Environment):
        """
        Executes the tool call using the provided environment.

        Args:
            env: The execution environment.

        Raises:
            Exception: If the execution fails.
        """
        raise NotImplementedError

    def try_execute(self, env: Environment) -> bool:
        """
        Attempts to execute the tool call, logging any exceptions.

        Args:
            env: The execution environment.

        Returns:
            True if execution succeeded, False otherwise.
        """
        try:
            self.execute(env)
            return True
        except Exception as e:
            env[ToolEnv].log(f"Error executing: {e}")
            return False

class InvalidToolCall(ToolCall):
    """
    Represents a failed tool call parse.
    """
    _error: Exception

    def __init__(self, error: Exception):
        self._error = error

    @property
    def title(self) -> str:
        return "invalid tool call"

    def execute(self, env: Environment):
        raise self._error

class Tool(ValueTypeMixin):
    """
    Marker interface for all tools.
    """
    pass

@cache
def standard_tools() -> tuple[Tool, ...]:
    """
    Returns a standard set of tools for file manipulation.

    The standard toolset includes tools for creating/updating files, moving
    files, removing files, and a fallback tool to skip generic code blocks.

    Returns:
        A tuple of standard tool instances.
    """
    from llobot.tools.code import DummyCodeBlockTool
    from llobot.tools.files import FileTool
    from llobot.tools.move import MoveTool
    from llobot.tools.remove import RemoveTool
    return (
        FileTool(),
        MoveTool(),
        RemoveTool(),
        DummyCodeBlockTool(),
    )


__all__ = [
    'Tool',
    'ToolCall',
    'InvalidToolCall',
    'standard_tools',
]
