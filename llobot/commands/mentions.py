"""
Parser for @command mentions in chat messages.
"""
from __future__ import annotations
import re
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch

_CODE_BLOCK_RE = re.compile(r'(`{3,}).*?\1', re.DOTALL)

# This regex finds all mentions and inline code spans.
# Mentions can be bare like @command, or quoted like @`command`.
# Quoted mentions can use single or double backticks.
# Bare mentions greedily match a set of characters.
# The regex also matches inline code spans to ensure they are skipped when parsing bare mentions.
# The order of alternatives is important to correctly identify tokens.
_UNIFIED_RE = re.compile(
    r"""
    # A mention must be preceded by whitespace or be at the start of a line.
    (?:^|\s)@
    (?:
        # A quoted mention with double backticks. It can contain single backticks.
        ``(?P<quoted_double>(?:[^`]|`[^`])*?)``
        |
        # A quoted mention with a single backtick. It cannot contain backticks or newlines.
        `(?P<quoted_single>[^`\n]*?)`
        |
        # A bare mention.
        (?P<bare>[a-zA-Z0-9-_/*?:=.]+)
    )
    |
    # An inline code span. This is matched to be ignored, effectively stripping it
    # from the text being considered for bare mentions. Quoted mentions are handled
    # by the more specific rule above.
    (?:
        ``(?:[^`]|`[^`])*?``
        |
        `[^`\n]*?`
    )
    """,
    re.VERBOSE
)

def parse_mentions(source: str | ChatMessage | ChatBranch) -> list[str]:
    """
    Parses @command mentions from a string, ChatMessage, or ChatBranch.

    It supports bare mentions (@command) and quoted mentions (@`command`).
    Markdown code blocks are stripped before parsing. Inline code spans are
    also ignored, so a bare mention inside a code span will not be detected.
    Mentions are returned in the order of their appearance.

    Args:
        source: The input to parse.

    Returns:
        A list of command strings found in the text.
    """
    if isinstance(source, ChatBranch):
        # Concatenate content from all messages in the branch.
        content = '\n'.join(m.content for m in source)
    elif isinstance(source, ChatMessage):
        content = source.content
    else:
        content = source

    # First, strip markdown code blocks entirely.
    content_without_blocks = _CODE_BLOCK_RE.sub('', content)

    mentions = []
    # Find all mentions and inline code spans in order.
    for match in _UNIFIED_RE.finditer(content_without_blocks):
        if match.group('quoted_double') is not None:
            # For quoted mentions, take the content and strip whitespace.
            command = match.group('quoted_double').strip()
        elif match.group('quoted_single') is not None:
            command = match.group('quoted_single').strip()
        elif match.group('bare') is not None:
            # For bare mentions, strip trailing dots and colons.
            command = match.group('bare').rstrip('.:')
        else:
            # If it is a code span, we just ignore it. The regex consumes it
            # so its content is not available for subsequent bare mention matching.
            continue

        # Skip empty commands.
        if command:
            mentions.append(command)

    return mentions

__all__ = [
    'parse_mentions',
]
