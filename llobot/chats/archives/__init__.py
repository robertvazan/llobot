"""
Storage for chat histories.

This package provides the `ChatArchive` interface for storing and retrieving
chat histories. Archives are organized into zones, which are simple string
identifiers. Within each zone, chats are stored by timestamp.

Submodules
----------
markdown
    An implementation of `ChatArchive` that stores chats as Markdown files.
"""
from __future__ import annotations
from datetime import datetime
from typing import Iterable
from pathlib import Path
from llobot.chats.branches import ChatBranch
from llobot.utils.zones import Zoning
from llobot.utils.fs import data_home

class ChatArchive:
    """
    An abstract base class for storing and retrieving chat histories.

    Chat archives are organized into zones, which are simple string identifiers.
    Within each zone, chats are stored by timestamp.
    """
    def add(self, zone: str, time: datetime, chat: ChatBranch):
        """
        Adds a chat to the archive.

        Args:
            zone: The zone to store the chat in.
            time: The timestamp for the chat.
            chat: The chat branch to store.
        """
        pass

    def scatter(self, zones: Iterable[str], time: datetime, chat: ChatBranch):
        """
        Adds the same chat to multiple zones.

        Implementations may use optimizations like hardlinks for efficiency.

        Args:
            zones: The zones to store the chat in.
            time: The timestamp for the chat.
            chat: The chat branch to store.
        """
        for zone in zones:
            self.add(zone, time, chat)

    def remove(self, zone: str, time: datetime):
        """
        Removes a chat from the archive.

        Args:
            zone: The zone where the chat is stored.
            time: The timestamp of the chat to remove.
        """
        pass

    def read(self, zone: str, time: datetime) -> ChatBranch | None:
        """
        Reads a specific chat from the archive.

        Args:
            zone: The zone where the chat is stored.
            time: The timestamp of the chat to read.

        Returns:
            The ChatBranch if found, otherwise None.
        """
        return None

    def contains(self, zone: str, time: datetime) -> bool:
        """
        Checks if a specific chat exists in the archive.

        Args:
            zone: The zone where the chat is stored.
            time: The timestamp of the chat to check.

        Returns:
            True if the chat exists, otherwise False.
        """
        return self.read(zone, time) is not None

    def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[tuple[datetime, ChatBranch]]:
        """
        Retrieves recent chats from a zone, newest first.

        Args:
            zone: The zone to retrieve chats from.
            cutoff: If specified, only chats at or before this time are returned.

        Returns:
            An iterable of (timestamp, ChatBranch) tuples.
        """
        return []

    def last(self, zone: str, cutoff: datetime | None = None) -> tuple[datetime | None, ChatBranch | None]:
        """
        Retrieves the most recent chat from a zone.

        Args:
            zone: The zone to retrieve the chat from.
            cutoff: If specified, the last chat at or before this time is returned.

        Returns:
            A (timestamp, ChatBranch) tuple, or (None, None) if the zone is empty.
        """
        last_item = next(self.recent(zone, cutoff), None)
        if last_item:
            return last_item
        return None, None

def standard_chat_archive(location: Zoning | Path | str = data_home()/'llobot/chats') -> ChatArchive:
    """
    Creates a standard chat archive using the markdown implementation.

    Args:
        location: The root directory or zoning configuration for the archive.

    Returns:
        A ChatArchive instance.
    """
    from llobot.chats.archives.markdown import MarkdownChatArchive
    return MarkdownChatArchive(location)

def coerce_chat_archive(what: ChatArchive | Zoning | Path | str) -> ChatArchive:
    """
    Coerces various types into a ChatArchive instance.

    If `what` is already a `ChatArchive`, it's returned as is.
    Otherwise, it's passed to `standard_chat_archive()` to create a new archive.

    Args:
        what: The object to coerce.

    Returns:
        A ChatArchive instance.
    """
    if isinstance(what, ChatArchive):
        return what
    else:
        return standard_chat_archive(what)

__all__ = [
    'ChatArchive',
    'standard_chat_archive',
    'coerce_chat_archive',
]
