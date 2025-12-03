"""
Dummy tool for skipping code blocks.
"""
from __future__ import annotations
import re
from llobot.tools import Tool, ToolCall

_CODE_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,})(?P<lang>\w*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*$',
    re.DOTALL | re.MULTILINE
)

class CodeBlockTool(Tool):
    """
    Matches generic code blocks to prevent them from being parsed as other tools,
    or simply to skip them.
    """
    def slice(self, source: str, at: int) -> int:
        match = _CODE_BLOCK_RE.match(source, pos=at)
        if not match:
            return 0
        return match.end() - at

    def parse(self, source: str) -> ToolCall | None:
        """
        This tool's purpose is to skip code blocks, so it returns None.
        """
        return None

__all__ = [
    'CodeBlockTool',
]
