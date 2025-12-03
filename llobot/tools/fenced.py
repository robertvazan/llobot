"""
Base class for tools using fenced code blocks.
"""
from __future__ import annotations
import re
from functools import cache
from llobot.tools import Tool, ToolCall

@cache
def _get_fenced_re(language: str) -> re.Pattern:
    """
    Returns a cached, compiled regex for a fenced code block with a specific language.
    """
    # Regex to capture a fenced code block with a specific language.
    # It captures the fence and content.
    # ^(?P<fence>`{3,}) captures the opening backticks at the start of a line.
    # {re.escape(language)} matches the specified language.
    # (?P<content>.*?) non-greedily captures the content.
    # ^(?P=fence) matches the closing fence on a new line.
    return re.compile(
        rf'^(?P<fence>`{{3,}}){re.escape(language)}\s*\n'
        r'(?P<content>.*?)'
        r'^(?P=fence)\s*$',
        re.DOTALL | re.MULTILINE
    )

class FencedTool(Tool):
    """
    A base tool that matches fenced code blocks with a specific language.

    It matches blocks like:
    ```language
    content
    ```
    """
    _language: str
    _re: re.Pattern

    def __init__(self, language: str = 'tool'):
        """
        Initializes a new FencedTool.

        Args:
            language: The language identifier for the fenced code block.
        """
        self._language = language
        self._re = _get_fenced_re(language)

    def slice(self, source: str, at: int) -> int:
        match = self._re.match(source, pos=at)
        if not match:
            return 0

        content = match.group('content').rstrip('\r\n')
        if not self.matches_content(content):
            return 0

        return match.end() - at

    def parse(self, source: str) -> ToolCall:
        match = self._re.fullmatch(source)
        assert match, "source for parse() must have been validated by slice()"

        content = match.group('content').rstrip('\r\n')
        return self.parse_content(content)

    def matches_content(self, source: str) -> bool:
        """
        Checks if the block content matches this tool's expected format.

        Args:
            source: The content inside the fenced block.

        Returns:
            True if it matches.
        """
        raise NotImplementedError

    def parse_content(self, source: str) -> ToolCall:
        """
        Parses the content into a ToolCall.

        Args:
            source: The content inside the fenced block.

        Returns:
            A ToolCall instance.
        """
        raise NotImplementedError

__all__ = [
    'FencedTool',
]
