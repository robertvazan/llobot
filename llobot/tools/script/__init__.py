"""
Script tool and its commands.
"""
from __future__ import annotations
from functools import cache
from typing import Iterable
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import Tool, ToolCall, InvalidToolCall
from llobot.tools.fenced import FencedTool

class ScriptItem(Tool):
    """
    Interface for tools that parse single lines within a tool script.
    """

    def matches(self, env: Environment, line: str) -> bool:
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

    def parse(self, env: Environment, line: str) -> ToolCall:
        """
        Parses a single line into a ToolCall.

        Args:
            env: The environment.
            line: The command line to parse.

        Returns:
            A ToolCall instance.
        """
        raise NotImplementedError

class ScriptTool(FencedTool):
    """
    A tool that executes multiple line-based commands within a fenced code block.
    It delegates parsing of each line to registered `ScriptItem`s.
    """
    def matches_content(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'Script'

    def parse_content(self, env: Environment, name: str, header: str, content: str) -> Iterable[ToolCall]:
        lines = content.splitlines()
        # Find all registered script items
        script_items = [t for t in env[ToolEnv].tools if isinstance(t, ScriptItem)]

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            matched = False
            for item in script_items:
                try:
                    if not item.matches(env, line):
                        continue
                except Exception:
                    # Treat exception as mismatch
                    continue

                try:
                    yield item.parse(env, line)
                except Exception as e:
                    yield InvalidToolCall(e)

                matched = True
                break

            if not matched:
                yield InvalidToolCall(ValueError(f"Unrecognized tool: {line}"))

@cache
def standard_script_tools() -> tuple[ScriptItem, ...]:
    """
    Returns the standard set of script items.
    """
    from llobot.tools.script.cat import ScriptCat
    from llobot.tools.script.move import ScriptMove
    from llobot.tools.script.remove import ScriptRemove
    from llobot.tools.script.replace import ScriptReplace
    return (
        ScriptCat(),
        ScriptMove(),
        ScriptRemove(),
        ScriptReplace(),
    )

__all__ = [
    'ScriptItem',
    'ScriptTool',
    'standard_script_tools',
]
