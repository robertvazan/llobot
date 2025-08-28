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
models
    A wrapper that exposes a `Role` as a `Model`.

Markdown files like `coder.md` and `editor.md` contain the core system
prompts for the respective roles.
"""
from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
import re
import llobot.time
from llobot.chats import ChatBranch
from llobot.chats.archives import ChatArchive
from llobot.projects import Project
from llobot.fs.zones import Zoning
from llobot.models import Model
import llobot.fs
import llobot.chats.archives

_logger = logging.getLogger(__name__)

_PROJECT_HEADER_RE = re.compile(r'~([a-zA-Z0-9_/.-]+)')

class Role:
    _name: str
    _model: Model
    _projects: dict[str, Project]
    _example_archive: ChatArchive

    def __init__(self, name: str, model: Model, *,
        projects: list[Project] | None = None,
        example_archive: ChatArchive | Zoning | Path | str = llobot.chats.archives.standard(llobot.fs.data()/'llobot/examples'),
    ):
        """
        Initializes the Role.

        Args:
            name: The name of the role.
            model: The language model to use.
            projects: A list of projects to be used as knowledge bases.
            example_archive: The archive for storing examples.
        """
        self._name = name
        self._model = model
        self._projects = {p.name: p for p in projects} if projects else {}
        self._example_archive = llobot.chats.archives.coerce(example_archive)

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> Model:
        return self._model

    @property
    def projects(self) -> dict[str, Project]:
        return self._projects

    @property
    def example_archive(self) -> ChatArchive:
        return self._example_archive

    def __str__(self) -> str:
        return self.name

    def resolve_project(self, prompt: ChatBranch) -> Project | None:
        """
        Parses the project name from the last line of the first message in a prompt.

        The project name is expected to be in the format `~project_name`.

        Args:
            prompt: The chat branch to parse.

        Returns:
            The resolved Project instance, or None if no project is specified.

        Raises:
            KeyError: If the specified project name is not found.
        """
        if not prompt:
            return None
        first_message = prompt[0].content
        lines = first_message.strip().splitlines()
        if not lines:
            return None
        last_line = lines[-1].strip()
        match = _PROJECT_HEADER_RE.fullmatch(last_line)
        if not match:
            return None
        project_name = match[1]
        if not project_name:
            return None
        project = self._projects.get(project_name)
        if not project:
            raise KeyError(f'No such project: {project_name}')
        return project

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

    def handle_ok(self, chat: ChatBranch, cutoff: datetime):
        project = self.resolve_project(chat)
        self.save_example(chat, project)

    def recent_examples(self, project: Project | None, cutoff: datetime | None = None) -> Iterable[ChatBranch]:
        for zone in self.zone_names(project):
            for time, chat in self.example_archive.recent(zone, cutoff):
                yield chat.as_example()

    # Returns the synthetic part of the prompt that is prepended to the user prompt.
    def stuff(self, *,
        prompt: ChatBranch,
    ) -> ChatBranch:
        return ChatBranch()

__all__ = [
    'Role',
]
