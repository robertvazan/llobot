"""
Dummy tool for skipping code blocks.
"""
from __future__ import annotations
import re
from llobot.environments import Environment
from llobot.tools.dummy import DummyTool
from llobot.tools.reader import ToolReader

_CODE_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,})(?P<lang>\w*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*$',
    re.DOTALL | re.MULTILINE
)

class DummyCodeBlockTool(DummyTool):
    """
    Matches generic code blocks to prevent them from being parsed as other tools,
    or simply to skip them.
    """
    def execute(self, env: Environment, reader: ToolReader) -> None:
        match = _CODE_BLOCK_RE.match(reader.source, pos=reader.position)
        if not match:
            return

        reader.skip(match.end() - reader.position)
        # No pass_tool() because skip() doesn't increment tool count

__all__ = [
    'DummyCodeBlockTool',
]
