from __future__ import annotations
import logging
from datetime import datetime
import llobot.time
from llobot.chats import ChatBranch, ChatMetadata
from llobot.chats.archives import ChatArchive
from llobot.projects import Scope

_logger = logging.getLogger(__name__)

class ExpertMemory:
    def __init__(self, name: str, *, chat_archive: ChatArchive, example_archive: ChatArchive):
        self._name = name
        self._chat_archive = chat_archive
        self._example_archive = example_archive

    @property
    def name(self) -> str:
        return self._name

    @property
    def chat_archive(self) -> ChatArchive:
        return self._chat_archive

    @property
    def example_archive(self) -> ChatArchive:
        return self._example_archive

    def __str__(self) -> str:
        return self.name

    def zone_name(self, scope: Scope | None) -> str:
        return f'{scope.name}-{self.name}' if scope else self.name

    def ancestry(self, scope: Scope | None) -> list[Scope]:
        return ([ancestor for ancestor in scope.ancestry] if scope else []) + [None]

    def _save(self, chat: ChatBranch, scope: Scope | None, write: Callable[[str, ChatBranch], None], log_prefix: str):
        chat = chat.with_metadata(chat.metadata | ChatMetadata(
            bot=self.name,
            project=scope.project.name if scope else None,
            scope=scope.name if scope and scope.parent else None,
            time=llobot.time.now(),
        ))
        zones = []
        for ancestor in self.ancestry(scope):
            zone = self.zone_name(ancestor)
            write(zone, chat)
            zones.append(zone)
        _logger.info(f"{log_prefix}: {', '.join(zones)}")

    # Chat must already have metadata with model, options, and cutoff.
    def save_chat(self, chat: ChatBranch, scope: Scope | None):
        def write(zone: str, chat: ChatBranch):
            self.chat_archive.add(zone, chat)
        self._save(chat, scope, write, "Archived chat")

    # Chat must already have metadata with model, options, and cutoff.
    def save_example(self, chat: ChatBranch, scope: Scope | None):
        def write(zone: str, chat: ChatBranch):
            last = self.example_archive.last(zone)
            # Replace the last example if it has the same prompt.
            if last and last.as_example()[0].content == chat.as_example()[0].content:
                self.example_archive.remove(zone, last.metadata.time)
            self.example_archive.add(zone, chat)
        self._save(chat, scope, write, "Archived example")

    def recent_examples(self, scope: Scope | None, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
        for chat in self.example_archive.recent(self.zone_name(scope), cutoff):
            yield chat.as_example().with_metadata(chat.metadata)

    def recent_ancestor_examples(self, scope: Scope | None, cutoff: datetime | None = None) -> list[Iterable[ChatBranch]]:
        return [self.recent_examples(ancestor, cutoff) for ancestor in self.ancestry(scope)]

    def has_example(self, scope: Scope | None, time: datetime) -> bool:
        return any(self.example_archive.contains(self.zone_name(ancestor), time) for ancestor in self.ancestry(scope))

def standard(name: str, *,
    chat_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/chats'),
    example_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/examples'),
) -> ExpertMemory:
    return ExpertMemory(name,
        chat_archive=llobot.chats.archives.coerce(chat_archive),
        example_archive=llobot.chats.archives.coerce(example_archive),
    )

__all__ = [
    'ExpertMemory',
    'standard',
]

