"""
Tools for llobot.

This package provides the `Tool` and `ToolCall` interfaces. Implementations
for various tools are available in submodules.

Submodules
----------
block
    Base class for tools that parse content blocks.
code
    A tool for skipping code blocks.
dummy
    Base class for tools that skip content.
patch
    A tool for patching files using unified diffs.
fenced
    Tools and base classes for tools that use fenced code blocks.
write
    A tool for creating or updating files from file listings.
parsing
    A function to parse tool calls from text.
execution
    A function to execute tool calls.
shell
    A tool for executing shell scripts.
script
    Package for the script tool and its commands (cat, mv, rm, sd).
"""
from __future__ import annotations
from functools import cache
from llobot.environments import Environment
from llobot.utils.values import ValueTypeMixin
from llobot.utils.text import quote_code

class ToolCall(ValueTypeMixin):
    """
    Represents a parsed tool call ready for execution.
    """

    @property
    def summary(self) -> str:
        """
        Returns a summary or header of the tool call.

        Example: "rm ~/path/to/file" or "Write: ~/path/to/file".
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
            from llobot.chats.intent import ChatIntent
            from llobot.chats.message import ChatMessage
            from llobot.environments.context import ContextEnv
            env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Error executing {self.summary}: {quote_code(str(e))}"))
            return False

class InvalidToolCall(ToolCall):
    """
    Represents a failed tool call parse.
    """
    _error: Exception
    _summary: str

    def __init__(self, error: Exception, summary: str = "invalid tool call"):
        self._error = error
        self._summary = summary

    @property
    def summary(self) -> str:
        return self._summary

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
    files, removing files, replacing text, reading files, and a fallback tool
    to skip generic code blocks.

    Returns:
        A tuple of standard tool instances.
    """
    from llobot.tools.code import DummyCodeBlockTool
    from llobot.tools.fenced import UnrecognizedFencedTool
    from llobot.tools.patch import PatchTool
    from llobot.tools.script import ScriptTool, standard_script_tools
    from llobot.tools.shell import ShellTool
    from llobot.tools.write import WriteTool
    return (
        WriteTool(),
        PatchTool(),
        ShellTool(),
        ScriptTool(),
        UnrecognizedFencedTool(),
        DummyCodeBlockTool(),
        *standard_script_tools(),
    )


__all__ = [
    'Tool',
    'ToolCall',
    'InvalidToolCall',
    'standard_tools',
]
