"""
Dummy tool for skipping code blocks.
"""
from __future__ import annotations
import re
from llobot.environments import Environment
from llobot.tools.dummy import DummyTool

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
    def skip(self, env: Environment, source: str, at: int) -> int:
        match = _CODE_BLOCK_RE.match(source, pos=at)
        if not match:
            return 0
        return match.end() - at

__all__ = [
    'DummyCodeBlockTool',
]
