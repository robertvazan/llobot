"""
Serialization of chat branches to and from Markdown format.

The format uses blockquotes to denote message metadata, like intent.
"""
import re
from pathlib import Path
from llobot.chats.intents import ChatIntent
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.messages import ChatMessage
from llobot.fs import read_text, write_text

_INTENT_RE = re.compile('> ([A-Z][-A-Za-z]*)')

def format_chat_as_markdown(chat: ChatBranch) -> str:
    """
    Serializes a chat branch into a Markdown string.

    Each message is preceded by a blockquote indicating its intent, e.g., `> Prompt`.

    Args:
        chat: The chat branch to format.

    Returns:
        The Markdown representation of the chat.
    """
    lines = []
    for message in chat:
        lines.append('')
        lines.append(f'> {message.intent}')
        lines.append('')
        for line in message.content.splitlines():
            matched = _INTENT_RE.fullmatch(line)
            if matched:
                lines.append(f'> Escaped-{matched.group(1)}')
            else:
                lines.append(line)
        if message.content.endswith('\n'):
            lines.append('')
    # Remove leading blank line if present
    if lines and not lines[0]:
        lines.pop(0)
    return ''.join([l + '\n' for l in lines])

def parse_chat_as_markdown(formatted: str) -> ChatBranch:
    """
    Parses a chat branch from its Markdown representation.

    This is the reverse of `format_chat_as_markdown()`.

    Args:
        formatted: The Markdown string to parse.

    Returns:
        The parsed chat branch.

    Raises:
        ValueError: If the format is invalid.
    """
    builder = ChatBuilder()
    intent = None
    lines = None
    first_message = True
    for line in formatted.splitlines():
        # Empty line before first message.
        if first_message and not intent and not line:
            continue
        matched = _INTENT_RE.fullmatch(line)
        if matched:
            if matched.group(1).startswith('Escaped-'):
                if not intent:
                    raise ValueError
                lines.append('> ' + matched.group(1).removeprefix('Escaped-'))
            else:
                if intent:
                    if len(lines) < 2 or lines[0] or lines[-1]:
                        raise ValueError
                    builder.add(ChatMessage(intent, '\n'.join(lines[1:-1])))
                intent = ChatIntent.parse(matched.group(1))
                lines = []
                first_message = False
        else:
            if not intent:
                # Tolerate content before first intent, for example old metadata format.
                continue
            lines.append(line)
    if intent:
        if len(lines) < 1 or lines[0]:
            raise ValueError
        builder.add(ChatMessage(intent, '\n'.join(lines[1:])))
    return builder.build()

def save_chat_as_markdown(path: Path, chat: ChatBranch):
    """
    Saves a chat branch to a Markdown file.

    Args:
        path: The path to the file.
        chat: The chat branch to save.
    """
    write_text(path, format_chat_as_markdown(chat))

def load_chat_as_markdown(path: Path) -> ChatBranch:
    """
    Loads a chat branch from a Markdown file.

    Args:
        path: The path to the file.

    Returns:
        The loaded chat branch.
    """
    return parse_chat_as_markdown(read_text(path))

__all__ = [
    'format_chat_as_markdown',
    'parse_chat_as_markdown',
    'save_chat_as_markdown',
    'load_chat_as_markdown',
]
