"""
Parser for @command mentions in chat messages.
"""
from __future__ import annotations
import re
from typing import Iterable
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread

_CODE_BLOCK_RE = re.compile(r'(`{3,}).*?\1', re.DOTALL)

# This regex finds all mentions and inline code spans.
# Mentions can be bare like @command, or quoted like @`command`.
# Quoted mentions can use single or double backticks.
# Bare mentions greedily match a set of characters.
# The regex also matches inline code spans to ensure they are skipped when parsing bare mentions.
# The order of alternatives is important to correctly identify tokens.
_UNIFIED_RE = re.compile(
    r"""
    # A mention must not be preceded by a word character (alphanumeric or underscore).
    (?<!\w)@
    (?:
        # A quoted mention with double backticks. It can contain single backticks.
        ``(?P<quoted_double>(?:[^`]|`[^`])*?)``
        |
        # A quoted mention with a single backtick. It cannot contain backticks or newlines.
        `(?P<quoted_single>[^`\n]*?)`
        |
        # A bare mention.
        (?P<bare>[a-zA-Z0-9-_/*?:=.~]+)
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

def parse_mentions(source: str | ChatMessage | ChatThread) -> list[str]:
    """
    Parses @command mentions from a string, ChatMessage, or ChatThread.

    It supports bare mentions (@command) and quoted mentions (@`command`).
    A mention can be preceded by whitespace, punctuation, or be at the start
    of a line, but not by a word character (e.g. in `email@domain.com`).
    Markdown code blocks are stripped before parsing. Inline code spans are
    also ignored, so a bare mention inside a code span will not be detected.
    Mentions are returned in the order of their appearance.

    Args:
        source: The input to parse.

    Returns:
        A list of command strings found in the text.
    """
    if isinstance(source, ChatThread):
        # Concatenate content from all messages in the thread.
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
            # For bare mentions, strip trailing dots, colons, question marks, and slashes.
            command = match.group('bare').rstrip('.:?/')
        else:
            # If it is a code span, we just ignore it. The regex consumes it
            # so its content is not available for subsequent bare mention matching.
            continue

        # Skip empty commands.
        if command:
            mentions.append(command)

    return mentions

# Regex part for a single mention, used for stripping.
_MENTION_STRIP_RE_PART = r"""
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

# Matches one or more mentions at the start of a string.
_LEADING_MENTIONS_RE = re.compile(
    r"^\s*(?:" + _MENTION_STRIP_RE_PART + r"\s*)+",
    re.VERBOSE
)
# Matches one or more mentions at the end of a string.
_TRAILING_MENTIONS_RE = re.compile(
    r"(?:\s+" + _MENTION_STRIP_RE_PART + r")+\s*$",
    re.VERBOSE
)

# Regex for filter_mentions. It matches code blocks (to preserve), mentions (to filter),
# and inline code (to preserve).
_FILTER_RE = re.compile(
    r"""
    # Code block: 3+ backticks, content, same backticks.
    (?P<block>`{3,}).*?(?P=block)
    |
    # A mention.
    (?<!\w)@
    (?:
        # A quoted mention with double backticks.
        ``(?P<quoted_double>(?:[^`]|`[^`])*?)``
        |
        # A quoted mention with a single backtick.
        `(?P<quoted_single>[^`\n]*?)`
        |
        # A bare mention.
        (?P<bare>[a-zA-Z0-9-_/*?:=.~]+)
    )
    |
    # An inline code span.
    (?:
        ``(?:[^`]|`[^`])*?``
        |
        `[^`\n]*?`
    )
    """,
    re.VERBOSE | re.DOTALL
)

def filter_mentions(text: str, mentions: Iterable[str]) -> str:
    """
    Removes specific mentions from the text.

    When a mention is removed, all horizontal whitespace following it on the same line
    is also removed. Code blocks and inline code spans are respected (mentions inside
    them are ignored).

    Args:
        text: The input text.
        mentions: An iterable of mention command strings to remove (e.g. "approve").

    Returns:
        The text with specified mentions removed.
    """
    target_set = set(mentions)
    result = []
    last_pos = 0

    for match in _FILTER_RE.finditer(text):
        # Append text before the match
        result.append(text[last_pos:match.start()])

        # Determine the command if it is a mention
        command = None
        if match.group('quoted_double') is not None:
            command = match.group('quoted_double').strip()
        elif match.group('quoted_single') is not None:
            command = match.group('quoted_single').strip()
        elif match.group('bare') is not None:
            command = match.group('bare').rstrip('.:?/')

        # If it's not a mention or not one of the target mentions, keep it.
        if command is None or command not in target_set:
            result.append(match.group(0))
            last_pos = match.end()
        else:
            # It is a target mention. Skip it.
            # Also skip following horizontal whitespace.
            end_pos = match.end()
            while end_pos < len(text) and text[end_pos] in ' \t':
                end_pos += 1
            last_pos = end_pos

    result.append(text[last_pos:])
    return ''.join(result)

def strip_mentions(text: str) -> str:
    """
    Strips leading and trailing @mentions from a string.

    This function removes mentions from the beginning and end of a string,
    along with any surrounding whitespace. Stripping stops when any
    non-mention, non-whitespace content is encountered.

    Args:
        text: The input string.

    Returns:
        The string with leading and trailing mentions removed, or an empty string
        if the input consists only of mentions and whitespace.
    """
    stripped_leading = _LEADING_MENTIONS_RE.sub('', text, count=1)
    stripped_both = _TRAILING_MENTIONS_RE.sub('', stripped_leading, count=1)
    return stripped_both.strip()

__all__ = [
    'parse_mentions',
    'filter_mentions',
    'strip_mentions',
]
