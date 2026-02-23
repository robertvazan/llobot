"""
Dummy tool for unrecognized fenced blocks.
"""
from __future__ import annotations
import re
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.tools.dummy import DummyTool
from llobot.tools.reader import ToolReader
from llobot.utils.text import quote_code

# Matches:
# <details>
# <summary>name: header</summary>
#
# ```lang
# content
# ```
#
# </details>
_FENCED_BLOCK_RE = re.compile(
    r'^<details>\s*<summary>\s*(?P<name>\w+):\s*(?P<header>.+?)\s*</summary>\s*'
    r'^(?P<fence>`{3,})(?P<lang>[^`\n]*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*</details>',
    re.DOTALL | re.MULTILINE
)

class UnrecognizedFencedTool(DummyTool):
    """
    A dummy tool that matches any fenced tool block and reports an error.
    """
    def execute(self, env: Environment, reader: ToolReader) -> None:
        match = _FENCED_BLOCK_RE.match(reader.source, pos=reader.position)
        if not match:
            return

        name = match.group('name')
        header = match.group('header').strip()

        # Advance/skip. Since this is a DummyTool, we use skip().
        # However, it reports an error status, so effectively it handles the block.
        reader.skip(match.end() - reader.position)

        env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, f"❌ Unrecognized tool '{name}' or invalid block format. Header: {quote_code(header)}"))

__all__ = [
    'UnrecognizedFencedTool',
]
