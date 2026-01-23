"""
Tools for llobot.

This package provides the `Tool` interface and standard toolset.

Submodules
----------
block
    Base class for tools that parse content blocks.
code
    A tool for skipping code blocks.
dummy
    Marker interface for tools that skip content.
patch
    A tool for patching files using unified diffs.
fenced
    Tools and base classes for tools that use fenced code blocks.
write
    A tool for creating or updating files from file listings.
execution
    A function to execute tool calls.
shell
    A tool for executing shell scripts.
script
    Package for the script tool and its commands (cat, mv, rm, sd).
reader
    Tool reader for tracking parsing position.
"""
from __future__ import annotations
from functools import cache
from llobot.utils.values import ValueTypeMixin

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
    'standard_tools',
]
