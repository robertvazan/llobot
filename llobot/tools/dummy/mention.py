"""
Dummy tool for warning about unsupported mentions in model responses.
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

# Regex part for a single mention.
# Matches @ followed by a quoted string or a bare mention.
# Bare mentions can contain alphanumeric characters, dashes, underscores, and various punctuation.
# This must be kept in sync with llobot/formats/mentions.py.
_MENTION_PATTERN = r"""
@(?:
    # A quoted mention with double backticks. It can contain single backticks.
    ``(?:[^`]|`[^`])*?``
    |
    # A quoted mention with a single backtick. It cannot contain backticks or newlines.
    `[^`\n]*?`
    |
    # A bare mention.
    [a-zA-Z0-9-_/*?:=.~]+
)
"""

# Allow leading whitespace (indentation) before the mention
_MENTION_AT_START_RE = re.compile(f"^[ \t]*(?P<mention>{_MENTION_PATTERN})", re.VERBOSE)

class DummyMentionTool(DummyTool):
    """
    Detects lines starting with @mentions and warns the user.
    """
    def execute(self, env: Environment, reader: ToolReader) -> None:
        source = reader.source
        pos = reader.position

        # Determine the line end
        try:
            line_end = source.index('\n', pos) + 1
        except ValueError:
            line_end = len(source)

        line = source[pos:line_end]

        # Check if the line starts with a mention
        match = _MENTION_AT_START_RE.match(line)
        if not match:
            return

        mention = match.group('mention')

        # Skip the whole line
        reader.skip(len(line))

        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"⚠️ Mentions like {quote_code(mention)} are not supported in model responses."))

__all__ = [
    'DummyMentionTool',
]
