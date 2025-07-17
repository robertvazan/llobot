from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
import llobot.time
from llobot.chats import ChatBranch, ChatMetadata, ChatBuilder, ChatIntent
from llobot.chats.archives import ChatArchive
from llobot.projects import Project
from llobot.fs.zones import Zoning
import llobot.fs
import llobot.chats.archives

_logger = logging.getLogger(__name__)

class Role:
    _name: str
    _example_archive: ChatArchive

    def __init__(self, name: str, *,
        example_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/examples'),
    ):
        self._name = name
        self._example_archive = llobot.chats.archives.coerce(example_archive)

    @property
    def name(self) -> str:
        return self._name

    @property
    def example_archive(self) -> ChatArchive:
        return self._example_archive

    def __str__(self) -> str:
        return self.name

    def zone_name(self, project: Project | None) -> str:
        return f'{project.name}-{self.name}' if project else self.name

    def zone_names(self, project: Project | None) -> list[str]:
        zones = []
        if project:
            zones.append(self.zone_name(project.root))
        zones.append(self.zone_name(None))
        return zones

    # Chat must already have metadata with model, options, and cutoff.
    def save_example(self, chat: ChatBranch, project: Project | None):
        # Replace the last example if it has the same prompt.
        for zone in self.zone_names(project):
            last = self.example_archive.last(zone)
            if last and last[0].content == chat[0].content:
                self.example_archive.remove(zone, last.metadata.time)

        chat = chat.with_metadata(chat.metadata | ChatMetadata(
            role=self.name,
            project=project.root.name if project else None,
            time=llobot.time.now(),
        ))
        zones = self.zone_names(project)
        self.example_archive.scatter(zones, chat)
        _logger.info(f"Archived example: {', '.join(zones)}")

    def recent_examples(self, project: Project | None, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
        for zone in self.zone_names(project):
            for chat in self.example_archive.recent(zone, cutoff):
                yield chat.as_example()

    # Returns the synthetic part of the prompt that is prepended to the user prompt.
    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> ChatBranch:
        return ChatBranch()

    def __call__(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> ChatBranch:
        return self.stuff(prompt=prompt, project=project, cutoff=cutoff, budget=budget)

__all__ = [
    'Role',
]
