from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
import llobot.time
from llobot.chats import ChatBranch, ChatMetadata
from llobot.chats.archives import ChatArchive
from llobot.projects import Project
from llobot.fs.zones import Zoning

_logger = logging.getLogger(__name__)

class RoleMemory:
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

    def zone_name(self, project: Project | None) -> str:
        return f'{project.name}-{self.name}' if project else self.name

    def zone_names(self, project: Project | None) -> Iterable[str]:
        if project:
            yield self.zone_name(project.root)
        yield self.zone_name(None)

    def _save(self, chat: ChatBranch, project: Project | None, archive: ChatArchive, log_prefix: str):
        chat = chat.with_metadata(chat.metadata | ChatMetadata(
            role=self.name,
            project=project.root.name if project else None,
            subproject=project.name if project and project.is_subproject else None,
            time=llobot.time.now(),
        ))
        # Strip context messages before saving to reduce storage and avoid redundant information.
        # The context can be regenerated from the metadata.
        chat = chat.strip_context()
        zones = list(self.zone_names(project))
        archive.scatter(zones, chat)
        _logger.info(f"{log_prefix}: {', '.join(zones)}")

    # Chat must already have metadata with model, options, and cutoff.
    def save_chat(self, chat: ChatBranch, project: Project | None):
        self._save(chat, project, self.chat_archive, "Archived chat")

    # Chat must already have metadata with model, options, and cutoff.
    def save_example(self, chat: ChatBranch, project: Project | None):
        # Replace the last example if it has the same prompt.
        for zone in self.zone_names(project):
            last = self.example_archive.last(zone)
            if last and last.as_example()[0].content == chat.as_example()[0].content:
                self.example_archive.remove(zone, last.metadata.time)
        self._save(chat, project, self.example_archive, "Archived example")

    def recent_examples(self, project: Project | None, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
        for zone in self.zone_names(project):
            for chat in self.example_archive.recent(zone, cutoff):
                yield chat.as_example().with_metadata(chat.metadata)

def standard(name: str, *,
    chat_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/chats'),
    example_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/examples'),
) -> RoleMemory:
    return RoleMemory(name,
        chat_archive=llobot.chats.archives.coerce(chat_archive),
        example_archive=llobot.chats.archives.coerce(example_archive),
    )

__all__ = [
    'RoleMemory',
    'standard',
]

