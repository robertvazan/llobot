from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime
from llobot.fs.zones import Zoning
from llobot.chats.branches import ChatBranch
import llobot.time
import llobot.fs
import llobot.fs.time
import llobot.fs.zones
import llobot.chats.markdown

_logger = logging.getLogger(__name__)

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

def markdown(location: Zoning | Path | str) -> ChatArchive:
    """
    Creates a chat archive that stores chats as Markdown files on the filesystem.

    Args:
        location: The root directory or zoning configuration for the archive.

    Returns:
        A ChatArchive instance.
    """
    location = llobot.fs.zones.coerce(location)
    class MarkdownChatArchive(ChatArchive):
        def _path(self, zone: str, time: datetime) -> Path:
            return llobot.fs.time.path(location[zone], time, llobot.chats.markdown.SUFFIX)
        def add(self, zone: str, time: datetime, chat: ChatBranch):
            llobot.chats.markdown.save(self._path(zone, time), chat)
        def scatter(self, zones: Iterable[str], time: datetime, chat: ChatBranch):
            zones = list(zones)
            if not zones:
                return
            self.add(zones[0], time, chat)
            for zone in zones[1:]:
                source_path = self._path(zones[0], time)
                target_path = self._path(zone, time)
                try:
                    llobot.fs.create_parents(target_path)
                    target_path.hardlink_to(source_path)
                except Exception as ex:
                    # Fall back to regular saving if hardlink fails
                    _logger.warning(f"Failed to create hardlink from {source_path} to {target_path}: {ex}")
                    self.add(zone, time, chat)
        def remove(self, zone: str, time: datetime):
            self._path(zone, time).unlink(missing_ok=True)
        def read(self, zone: str, time: datetime) -> ChatBranch | None:
            path = self._path(zone, time)
            return llobot.chats.markdown.load(path) if path.exists() else None
        def contains(self, zone: str, time: datetime) -> bool:
            return self._path(zone, time).exists()
        def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[tuple[datetime, ChatBranch]]:
            for path in llobot.fs.time.recent(location[zone], llobot.chats.markdown.SUFFIX, cutoff):
                yield (llobot.fs.time.parse(path), llobot.chats.markdown.load(path))
    return MarkdownChatArchive()

def standard(location: Zoning | Path | str) -> ChatArchive:
    """
    Creates a standard chat archive using the markdown implementation.

    Args:
        location: The root directory or zoning configuration for the archive.

    Returns:
        A ChatArchive instance.
    """
    return markdown(location)

def coerce(what: ChatArchive | Zoning | Path | str) -> ChatArchive:
    """
    Coerces various types into a ChatArchive instance.

    If `what` is already a `ChatArchive`, it's returned as is.
    Otherwise, it's passed to `standard()` to create a new archive.

    Args:
        what: The object to coerce.

    Returns:
        A ChatArchive instance.
    """
    if isinstance(what, ChatArchive):
        return what
    else:
        return standard(what)

def rename(mapping: Callable[[str], str], underlying: ChatArchive) -> ChatArchive:
    """
    Wraps a chat archive, renaming zones before passing them to the underlying archive.

    Args:
        mapping: A function that takes a zone name and returns a new name.
        underlying: The chat archive to wrap.

    Returns:
        A new ChatArchive that uses the renamed zones.
    """
    class RenamingChatArchive(ChatArchive):
        def add(self, zone: str, time: datetime, chat: ChatBranch):
            underlying.add(mapping(zone), time, chat)
        def scatter(self, zones: Iterable[str], time: datetime, chat: ChatBranch):
            underlying.scatter([mapping(zone) for zone in zones], time, chat)
        def remove(self, zone: str, time: datetime):
            underlying.remove(mapping(zone), time)
        def read(self, zone: str, time: datetime) -> ChatBranch | None:
            return underlying.read(mapping(zone), time)
        def contains(self, zone: str, time: datetime) -> bool:
            return underlying.contains(mapping(zone), time)
        def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[tuple[datetime, ChatBranch]]:
            return underlying.recent(mapping(zone), cutoff)
    return RenamingChatArchive()

__all__ = [
    'ChatArchive',
    'markdown',
    'standard',
    'coerce',
    'rename',
]
