"""
Tools for llobot.

This package provides the `Tool` and `ToolCall` interfaces. Implementations
for various tools are available in submodules.

Submodules
----------
block
    Base class for tools that parse content blocks.
cat
    A tool for reading files.
code
    A tool for skipping code blocks.
dummy
    Base class for tools that skip content.
edit
    A tool for editing files using search and replace (legacy).
patch
    A tool for patching files using unified diffs.
fenced
    A base class for tools that use fenced code blocks.
write
    A tool for creating or updating files from file listings.
line
    Base class for tools that parse single lines.
move
    A tool for moving files.
parsing
    A function to parse tool calls from text.
remove
    A tool for removing files.
replace
    A tool for replacing text using regex patterns.
script
    A tool for executing scripts of line-based commands.
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

        Example: "rm path/to/file" or "write path/to/file".
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
    files, removing files, replacing text, reading files, and a fallback tool
    to skip generic code blocks.

    Returns:
        A tuple of standard tool instances.
    """
    from llobot.tools.cat import CatTool
    from llobot.tools.code import DummyCodeBlockTool
    from llobot.tools.patch import PatchTool
    from llobot.tools.move import MoveTool
    from llobot.tools.remove import RemoveTool
    from llobot.tools.replace import ReplaceTool
    from llobot.tools.script import ScriptTool
    from llobot.tools.write import WriteTool
    return (
        WriteTool(),
        PatchTool(),
        MoveTool(),
        RemoveTool(),
        ReplaceTool(),
        CatTool(),
        ScriptTool(),
        DummyCodeBlockTool(),
    )


__all__ = [
    'Tool',
    'ToolCall',
    'InvalidToolCall',
    'standard_tools',
]
