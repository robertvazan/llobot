"""
Tools using fenced code blocks wrapped in details/summary.

This module provides the `FencedTool` base class and the `UnrecognizedFencedTool`
fallback tool.
"""
from __future__ import annotations
import re
from typing import Iterable
from llobot.environments import Environment
from llobot.tools.dummy import DummyTool
from llobot.tools import ToolCall, InvalidToolCall
from llobot.tools.block import BlockTool

# Matches:
# <details>
# <summary>name: header</summary>
#
# ```lang
# content
# ```
#
# </details>
_DETAILS_BLOCK_RE = re.compile(
    r'^<details>\s*<summary>\s*(?P<name>\w+):\s*(?P<header>.+?)\s*</summary>\s*'
    r'^(?P<fence>`{3,})(?P<lang>[^`\n]*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*</details>',
    re.DOTALL | re.MULTILINE
)

class FencedTool(BlockTool):
    """
    A base tool that matches fenced code blocks wrapped in details/summary tags.
    """

    def slice(self, env: Environment, source: str, at: int) -> int:
        match = _DETAILS_BLOCK_RE.match(source, pos=at)
        if not match:
            return 0

        name = match.group('name')
        header = match.group('header').strip()
        content = match.group('content')

        if not self.matches_content(env, name, header, content):
            return 0

        return match.end() - at

    def parse(self, env: Environment, source: str) -> Iterable[ToolCall]:
        match = _DETAILS_BLOCK_RE.fullmatch(source)
        assert match, "source for parse() must have been validated by slice()"

        name = match.group('name')
        header = match.group('header').strip()
        fence = match.group('fence')
        content = match.group('content')

        # Perform ambiguous fence check directly in FencedTool
        fence_length = len(fence)
        if re.search(r'^`{%d,}' % fence_length, content, re.MULTILINE):
            summary = f"{name}: {header}"
            yield InvalidToolCall(
                ValueError(f"Content contains a line starting with {fence_length} or more backticks. Enclose the block in more backticks."),
                summary
            )
            return

        yield from self.parse_content(env, name, header, content)

    def matches_content(self, env: Environment, name: str, header: str, content: str) -> bool:
        """
        Checks if the block content matches this tool's expected format.

        Args:
            env: The environment.
            name: The tool name from the summary.
            header: The header from the summary.
            content: The content inside the fenced block.

        Returns:
            True if it matches.
        """
        return False

    def parse_content(self, env: Environment, name: str, header: str, content: str) -> Iterable[ToolCall]:
        """
        Parses the content into ToolCalls.

        Args:
            env: The environment.
            name: The tool name from the summary.
            header: The header from the summary.
            content: The content inside the fenced block.

        Returns:
            An iterable of ToolCall instances.
        """
        raise NotImplementedError

class UnrecognizedFencedTool(DummyTool):
    """
    A dummy tool that matches any fenced tool block and reports an error.
    """
    def skip(self, env: Environment, source: str, at: int) -> int:
        match = _DETAILS_BLOCK_RE.match(source, pos=at)
        if not match:
            return 0

        from llobot.chats.intent import ChatIntent
        from llobot.chats.message import ChatMessage
        from llobot.environments.context import ContextEnv

        name = match.group('name')
        header = match.group('header').strip()
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Unrecognized tool '{name}' or invalid block format. Header: {header}"))
        return match.end() - at

__all__ = [
    'FencedTool',
    'UnrecognizedFencedTool',
]
