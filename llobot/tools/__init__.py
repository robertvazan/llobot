"""
Tools for llobot.

This package provides the `Tool` and `ToolCall` interfaces. Implementations
for various tools are available in submodules.

Submodules
----------
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

class Tool:
    """
    Interface for parsing tool calls from text.
    """

    def slice(self, source: str, at: int) -> int:
        """
        Attempts to locate a tool call starting at the given position.

        It is assumed that `at` is an index pointing to the start of a line.

        Args:
            source: The source text.
            at: The index to start looking from.

        Returns:
            The length of the matching tool call substring, or 0 if no match.
            The returned slice does not need to include a trailing newline.
        """
        raise NotImplementedError

    def parse(self, source: str) -> ToolCall | None:
        """
        Parses a source string into a `ToolCall`.

        This method is only called with a `source` string that has been
        successfully matched by `slice()`.

        Args:
            source: The string identified by `slice`.

        Returns:
            A `ToolCall` instance, or `None` to indicate that this tool call
            should be silently skipped.
        """
        raise NotImplementedError

    def try_parse(self, source: str) -> ToolCall | None:
        """
        Attempts to parse a source string, returning an invalid call on failure.

        Args:
            source: The string identified by `slice`.

        Returns:
            A `ToolCall`, `InvalidToolCall`, or `None`.
        """
        try:
            return self.parse(source)
        except Exception as e:
            return InvalidToolCall(e)

__all__ = [
    'Tool',
    'ToolCall',
    'InvalidToolCall',
]
