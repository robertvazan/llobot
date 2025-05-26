from __future__ import annotations
from datetime import datetime
from llobot.fs.zones import Zoning
from llobot.chats import ChatBranch
import llobot.time
import llobot.fs
import llobot.fs.time
import llobot.fs.zones
import llobot.chats.markdown

class ChatArchive:
    def add(self, zone: str, chat: ChatBranch):
        pass

    def remove(self, zone: str, time: datetime):
        pass

    def read(self, zone: str, time: datetime) -> ChatBranch | None:
        return None

    def contains(self, zone: str, time: datetime) -> bool:
        return self.read(zone, time) is not None

    def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
        return []

    def last(self, zone: str, cutoff: datetime | None = None) -> ChatBranch | None:
        return next(self.recent(zone, cutoff), None)

def markdown(location: Zoning | Path | str) -> ChatArchive:
    location = llobot.fs.zones.coerce(location)
    class MarkdownChatArchive(ChatArchive):
        def _path(self, zone: str, time: datetime):
            return llobot.fs.time.path(location[zone], time, llobot.chats.markdown.SUFFIX)
        def add(self, zone: str, chat: ChatBranch):
            llobot.chats.markdown.save(self._path(zone, chat.metadata.time), chat)
        def remove(self, zone: str, time: datetime):
            self._path(zone, time).unlink(missing_ok=True)
        def read(self, zone: str, time: datetime) -> ChatBranch | None:
            path = self._path(zone, time)
            return llobot.chats.markdown.load(path) if path.exists() else None
        def contains(self, zone: str, time: datetime) -> bool:
            return self._path(zone, time).exists()
        def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
            for path in llobot.fs.time.recent(location[zone], llobot.chats.markdown.SUFFIX, cutoff):
                yield llobot.chats.markdown.load(path)
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
        def add(self, zone: str, chat: ChatBranch):
            underlying.add(mapping(zone), chat)
        def remove(self, zone: str, time: datetime):
            underlying.remove(mapping(zone), time)
        def read(self, zone: str, time: datetime) -> ChatBranch | None:
            return underlying.read(mapping(zone), time)
        def contains(self, zone: str, time: datetime) -> bool:
            return underlying.contains(mapping(zone), time)
        def recent(self, zone: str, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
            return underlying.recent(mapping(zone), cutoff)
    return RenamingChatArchive()

__all__ = [
    'ChatArchive',
    'markdown',
    'standard',
    'coerce',
    'rename',
]

