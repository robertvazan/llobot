"""
Tool for executing a script of line-based commands.
"""
from __future__ import annotations
from typing import Iterable
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import ToolCall, InvalidToolCall
from llobot.tools.fenced import FencedTool
from llobot.tools.line import LineTool

class ScriptTool(FencedTool):
    """
    A tool that executes multiple line-based commands within a fenced code block.

    It uses `toolscript` as the default language. It delegates parsing of each
    line to registered `LineTool`s.
    """
    def __init__(self):
        super().__init__('toolscript')

    def matches_content(self, env: Environment, source: str) -> bool:
        # We accept any content that parses as a fenced block, and validate lines later.
        return True

    def parse_content(self, env: Environment, source: str) -> Iterable[ToolCall]:
        lines = source.splitlines()
        # Find all registered line tools
        line_tools = [t for t in env[ToolEnv].tools if isinstance(t, LineTool)]

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            matched = False
            for tool in line_tools:
                try:
                    if not tool.matches_line(env, line):
                        continue
                except Exception:
                    # Treat exception as mismatch
                    continue

                try:
                    yield tool.parse_line(env, line)
                except Exception as e:
                    yield InvalidToolCall(e)

                matched = True
                break

            if not matched:
                yield InvalidToolCall(ValueError(f"Unrecognized tool: {line}"))

__all__ = [
    'ScriptTool',
]
