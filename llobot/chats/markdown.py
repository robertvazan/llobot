"""
An implementation of `ChatHistory` that stores chats as Markdown files.
"""
from __future__ import annotations
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Iterable
from llobot.utils.zones import Zoning, coerce_zoning
from llobot.chats.thread import ChatThread
from llobot.utils.fs import create_parents, read_text, write_text
from llobot.utils.history import format_history_path, parse_history_path, recent_history_paths
from llobot.chats.history import ChatHistory
from llobot.chats.intent import ChatIntent
from llobot.chats.builder import ChatBuilder
from llobot.chats.message import ChatMessage
from llobot.utils.values import ValueTypeMixin

_logger = logging.getLogger(__name__)
_INTENT_RE = re.compile('> ([A-Z][-A-Za-z]*)')

class MarkdownChatHistory(ChatHistory, ValueTypeMixin):
    """
    A chat history that stores chats as Markdown files on the filesystem.
    """
    _location: Zoning

    def __init__(self, location: Zoning | Path | str):
        """
        Creates a new markdown-based chat history.

        Args:
            location: The root directory or zoning configuration for the history.
        """
        self._location = coerce_zoning(location)

    def _path(self, zone: Path, time: datetime) -> Path:
        return format_history_path(self._location[zone], time, '.md')

    def add(self, zone: Path, time: datetime, chat: ChatThread):
        save_chat_to_markdown(self._path(zone, time), chat)

    def scatter(self, zones: Iterable[Path], time: datetime, chat: ChatThread):
        zones = list(zones)
        if not zones:
            return
        self.add(zones[0], time, chat)
        for zone in zones[1:]:
            source_path = self._path(zones[0], time)
            target_path = self._path(zone, time)
            try:
                create_parents(target_path)
                target_path.hardlink_to(source_path)
            except Exception as ex:
                # Fall back to regular saving if hardlink fails
                _logger.warning(f"Failed to create hardlink from {source_path} to {target_path}: {ex}")
                self.add(zone, time, chat)

    def remove(self, zone: Path, time: datetime):
        self._path(zone, time).unlink(missing_ok=True)

    def read(self, zone: Path, time: datetime) -> ChatThread | None:
        path = self._path(zone, time)
        return load_chat_from_markdown(path) if path.exists() else None

    def contains(self, zone: Path, time: datetime) -> bool:
        return self._path(zone, time).exists()

    def recent(self, zone: Path, cutoff: datetime | None = None) -> Iterable[tuple[datetime, ChatThread]]:
        for path in recent_history_paths(self._location[zone], '.md', cutoff):
            yield (parse_history_path(path), load_chat_from_markdown(path))

def format_chat_as_markdown(chat: ChatThread) -> str:
    """
    Serializes a chat thread into a Markdown string.

    Each message is preceded by a blockquote indicating its intent, e.g., `> Prompt`.

    Args:
        chat: The chat thread to format.

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

def parse_chat_from_markdown(formatted: str) -> ChatThread:
    """
    Parses a chat thread from its Markdown representation.

    This is the reverse of `format_chat_as_markdown()`.

    Args:
        formatted: The Markdown string to parse.

    Returns:
        The parsed chat thread.

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

def save_chat_to_markdown(path: Path, chat: ChatThread):
    """
    Saves a chat thread to a Markdown file.

    Args:
        path: The path to the file.
        chat: The chat thread to save.
    """
    write_text(path, format_chat_as_markdown(chat))

def load_chat_from_markdown(path: Path) -> ChatThread:
    """
    Loads a chat thread from a Markdown file.

    Args:
        path: The path to the file.

    Returns:
        The loaded chat thread.
    """
    return parse_chat_from_markdown(read_text(path))

__all__ = [
    'MarkdownChatHistory',
    'format_chat_as_markdown',
    'parse_chat_from_markdown',
    'save_chat_to_markdown',
    'load_chat_from_markdown',
]
