"""
Definitions of different bot personalities and capabilities.

This package defines the `Role` class, which encapsulates the logic for
assembling the context for a large language model. Each role has an associated
model and defines how to "stuff" the context with system prompts, knowledge,
and examples.

Submodules
----------

assistant
    A general-purpose assistant role.
coder
    A role specialized for software development tasks.
editor
    A role for editing and analyzing files, serving as a base for Coder.

Markdown files like `coder.md` and `editor.md` contain the core system
prompts for the respective roles.
"""
from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
import llobot.time
from llobot.chats import ChatBranch
from llobot.chats.archives import ChatArchive
from llobot.projects import Project
from llobot.fs.zones import Zoning
from llobot.models import Model
import llobot.fs
import llobot.chats.archives

_logger = logging.getLogger(__name__)

class Role:
    _name: str
    _model: Model
    _example_archive: ChatArchive

    def __init__(self, name: str, model: Model, *,
        example_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/examples'),
    ):
        self._name = name
        self._model = model
        self._example_archive = llobot.chats.archives.coerce(example_archive)

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> Model:
        return self._model

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
            zones.append(self.zone_name(project))
        zones.append(self.zone_name(None))
        return zones

    def save_example(self, chat: ChatBranch, project: Project | None):
        # Replace the last example if it has the same prompt.
        for zone in self.zone_names(project):
            last_time, last_chat = self.example_archive.last(zone)
            if last_chat and last_chat[0].content == chat[0].content:
                self.example_archive.remove(zone, last_time)

        time = llobot.time.now()
        zones = self.zone_names(project)
        self.example_archive.scatter(zones, time, chat)
        _logger.info(f"Archived example: {', '.join(zones)}")

    def handle_ok(self, chat: ChatBranch, project: Project | None, cutoff: datetime):
        self.save_example(chat, project)

    def recent_examples(self, project: Project | None, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
        for zone in self.zone_names(project):
            for time, chat in self.example_archive.recent(zone, cutoff):
                yield chat.as_example()

    # Returns the synthetic part of the prompt that is prepended to the user prompt.
    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
    ) -> ChatBranch:
        return ChatBranch()

__all__ = [
    'Role',
]
