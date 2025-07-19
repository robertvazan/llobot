from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime
from llobot.fs.zones import Zoning
from llobot.chats import ChatBranch
import llobot.time
import llobot.fs
import llobot.fs.time
import llobot.fs.zones
import llobot.chats.markdown

_logger = logging.getLogger(__name__)

class ChatArchive:
    def add(self, zone: str, time: datetime, chat: ChatBranch):
        pass

    def scatter(self, zones: Iterable[str], time: datetime, chat: ChatBranch):
        """Add the same chat to multiple zones, potentially using hardlinks for efficiency."""
        for zone in zones:
            self.add(zone, time, chat)

    def remove(self, zone: str, time: datetime):
        pass

    def read(self, zone: str, time: datetime) -> ChatBranch | None:
        return None

    def contains(self, zone: str, time: datetime) -> bool:
        return self.read(zone, time) is not None

    def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[tuple[datetime, ChatBranch]]:
        return []

    def last(self, zone: str, cutoff: datetime | None = None) -> tuple[datetime | None, ChatBranch | None]:
        last_item = next(self.recent(zone, cutoff), None)
        if last_item:
            return last_item
        return None, None

def markdown(location: Zoning | Path | str) -> ChatArchive:
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
    return markdown(location)

def coerce(what: ChatArchive | Zoning | Path | str) -> ChatArchive:
    if isinstance(what, ChatArchive):
        return what
    else:
        return standard(what)

def rename(mapping: Callable[[str], str], underlying: ChatArchive) -> ChatArchive:
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
