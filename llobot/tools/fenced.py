"""
Base class for tools using fenced code blocks.
"""
from __future__ import annotations
import re
from typing import Iterable
from llobot.environments import Environment
from llobot.tools import ToolCall
from llobot.tools.block import BlockTool

# Global regex for any fenced code block.
# ^(?P<fence>`{3,}) captures the opening backticks at the start of a line.
# (?P<lang>[^`\n]*) matches any language identifier (optional).
# (?P<content>.*?) non-greedily captures the content.
# ^(?P=fence) matches the closing fence on a new line.
_FENCED_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,})(?P<lang>[^`\n]*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*$',
    re.DOTALL | re.MULTILINE
)

class FencedTool(BlockTool):
    """
    A base tool that matches fenced code blocks.

    It matches blocks like:
    ```language
    content
    ```
    If language is None, it matches blocks with any language identifier (or none).
    """
    _language: str | None

    def __init__(self, language: str | None = 'tool'):
        """
        Initializes a new FencedTool.

        Args:
            language: The language identifier for the fenced code block. If None, any language is accepted.
        """
        self._language = language

    def slice(self, env: Environment, source: str, at: int) -> int:
        match = _FENCED_BLOCK_RE.match(source, pos=at)
        if not match:
            return 0

        # Check language matching if a specific language is required
        if self._language is not None:
            if match.group('lang') != self._language:
                return 0

        content = match.group('content').rstrip('\r\n')
        if not self.matches_content(env, content):
            return 0

        return match.end() - at

    def parse(self, env: Environment, source: str) -> Iterable[ToolCall]:
        match = _FENCED_BLOCK_RE.fullmatch(source)
        assert match, "source for parse() must have been validated by slice()"

        content = match.group('content').rstrip('\r\n')
        return self.parse_content(env, content)

    def matches_content(self, env: Environment, source: str) -> bool:
        """
        Checks if the block content matches this tool's expected format.

        Args:
            env: The environment.
            source: The content inside the fenced block.

        Returns:
            True if it matches.
        """
        raise NotImplementedError

    def parse_content(self, env: Environment, source: str) -> Iterable[ToolCall]:
        """
        Parses the content into ToolCalls.

        Args:
            env: The environment.
            source: The content inside the fenced block.

        Returns:
            An iterable of ToolCall instances.
        """
        raise NotImplementedError

__all__ = [
    'FencedTool',
]
