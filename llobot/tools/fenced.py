"""
Tools using fenced code blocks wrapped in details/summary.

This module provides the `FencedTool` base class and the `UnrecognizedFencedTool`
fallback tool.
"""
from __future__ import annotations
import re
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.tools.block import BlockTool
from llobot.tools.dummy import DummyTool
from llobot.tools.reader import ToolReader

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

    def execute(self, env: Environment, reader: ToolReader) -> None:
        match = _DETAILS_BLOCK_RE.match(reader.source, pos=reader.position)
        if not match:
            return

        name = match.group('name')
        header = match.group('header').strip()
        fence = match.group('fence')
        content = match.group('content')

        if not self.match_fenced(env, name, header, content):
            return

        # Advance reader to consume the block
        reader.advance(match.end() - reader.position)

        # Perform ambiguous fence check
        fence_length = len(fence)
        if re.search(r'^`{%d,}' % fence_length, content, re.MULTILINE):
            raise ValueError(f"Content contains a line starting with {fence_length} or more backticks. Enclose the block in more backticks.")

        if self.execute_fenced(env, name, header, content):
            reader.passed()

    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
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

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        """
        Executes the tool logic with the parsed content.

        Args:
            env: The environment.
            name: The tool name from the summary.
            header: The header from the summary.
            content: The content inside the fenced block.

        Returns:
            True if execution succeeded, False otherwise.
        """
        raise NotImplementedError


class UnrecognizedFencedTool(DummyTool):
    """
    A dummy tool that matches any fenced tool block and reports an error.
    """
    def execute(self, env: Environment, reader: ToolReader) -> None:
        match = _DETAILS_BLOCK_RE.match(reader.source, pos=reader.position)
        if not match:
            return

        name = match.group('name')
        header = match.group('header').strip()

        # Advance/skip. Since this is a DummyTool, we use skip().
        # However, it reports an error status, so effectively it handles the block.
        reader.skip(match.end() - reader.position)

        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Unrecognized tool '{name}' or invalid block format. Header: {header}"))

__all__ = [
    'FencedTool',
    'UnrecognizedFencedTool',
]
