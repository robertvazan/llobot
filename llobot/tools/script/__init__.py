"""
Script tool and its commands.
"""
from __future__ import annotations
from functools import cache
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import Tool
from llobot.tools.fenced import FencedTool

class ScriptItem(Tool):
    """
    Interface for tools that parse single lines within a tool script.
    """

    def execute(self, env: Environment, line: str) -> bool:
        """
        Attempts to execute a script command line.

        Args:
            env: The environment.
            line: The command line to execute.

        Returns:
            True if the command was recognized and executed (or attempted).
            False if the command did not match this item.

        Raises:
            Exception: If execution fails.
        """
        raise NotImplementedError

class ScriptTool(FencedTool):
    """
    A tool that executes multiple line-based commands within a fenced code block.
    It delegates parsing of each line to registered `ScriptItem`s.
    """
    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'Script'

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
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
                    if item.execute(env, line):
                        matched = True
                        break
                except Exception:
                    # If execute raises, it means it matched but failed. Propagate.
                    raise

            if not matched:
                raise ValueError(f"Unrecognized script command: {line}")
        return True

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
