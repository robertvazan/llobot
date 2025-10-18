"""
Storage for chat histories.

This package provides the `ChatHistory` interface for storing and retrieving
chat histories. Histories are organized into zones, which are relative paths.
Within each zone, chats are stored by timestamp.
"""
from __future__ import annotations
from datetime import datetime
from typing import Iterable
from pathlib import Path
from llobot.chats.thread import ChatThread
from llobot.utils.zones import Zoning
from llobot.utils.fs import data_home

class ChatHistory:
    """
    An abstract base class for storing and retrieving chat histories.

    Chat histories are organized into zones, which are relative paths.
    Within each zone, chats are stored by timestamp.
    """
    def add(self, zone: Path, time: datetime, chat: ChatThread):
        """
        Adds a chat to the history.

        Args:
            zone: The zone (a relative path) to store the chat in.
            time: The timestamp for the chat.
            chat: The chat thread to store.
        """
        pass

    def scatter(self, zones: Iterable[Path], time: datetime, chat: ChatThread):
        """
        Adds the same chat to multiple zones.

        Implementations may use optimizations like hardlinks for efficiency.

        Args:
            zones: The zones to store the chat in.
            time: The timestamp for the chat.
            chat: The chat thread to store.
        """
        for zone in zones:
            self.add(zone, time, chat)

    def remove(self, zone: Path, time: datetime):
        """
        Removes a chat from the history.

        Args:
            zone: The zone (a relative path) where the chat is stored.
            time: The timestamp of the chat to remove.
        """
        pass

    def read(self, zone: Path, time: datetime) -> ChatThread | None:
        """
        Reads a specific chat from the history.

        Args:
            zone: The zone (a relative path) where the chat is stored.
            time: The timestamp of the chat to read.

        Returns:
            The ChatThread if found, otherwise None.
        """
        return None

    def contains(self, zone: Path, time: datetime) -> bool:
        """
        Checks if a specific chat exists in the history.

        Args:
            zone: The zone (a relative path) where the chat is stored.
            time: The timestamp of the chat to check.

        Returns:
            True if the chat exists, otherwise False.
        """
        return self.read(zone, time) is not None

    def recent(self, zone: Path, cutoff: datetime | None = None) -> Iterable[tuple[datetime, ChatThread]]:
        """
        Retrieves recent chats from a zone, newest first.

        Args:
            zone: The zone (a relative path) to retrieve chats from.
            cutoff: If specified, only chats at or before this time are returned.

        Returns:
            An iterable of (timestamp, ChatThread) tuples.
        """
        return []

    def last(self, zone: Path, cutoff: datetime | None = None) -> tuple[datetime | None, ChatThread | None]:
        """
        Retrieves the most recent chat from a zone.

        Args:
            zone: The zone (a relative path) to retrieve the chat from.
            cutoff: If specified, the last chat at or before this time is returned.

        Returns:
            A (timestamp, ChatThread) tuple, or (None, None) if the zone is empty.
        """
        last_item = next(self.recent(zone, cutoff), None)
        if last_item:
            return last_item
        return None, None

def standard_chat_history(location: Zoning | Path | str = data_home()/'llobot/chats') -> ChatHistory:
    """
    Creates a standard chat history using the markdown implementation.

    Args:
        location: The root directory or zoning configuration for the history.

    Returns:
        A ChatHistory instance.
    """
    from llobot.chats.markdown import MarkdownChatHistory
    return MarkdownChatHistory(location)

def coerce_chat_history(what: ChatHistory | Zoning | Path | str) -> ChatHistory:
    """
    Coerces various types into a ChatHistory instance.

    If `what` is already a `ChatHistory`, it's returned as is.
    Otherwise, it's passed to `standard_chat_history()` to create a new history.

    Args:
        what: The object to coerce.

    Returns:
        A ChatHistory instance.
    """
    if isinstance(what, ChatHistory):
        return what
    else:
        return standard_chat_history(what)

__all__ = [
    'ChatHistory',
    'standard_chat_history',
    'coerce_chat_history',
]
