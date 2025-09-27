from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable
from heapq import merge
from itertools import chain
from llobot.chats.archives import ChatArchive, standard_chat_archive, coerce_chat_archive
from llobot.chats.binarization import binarize_intent
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.utils.fs import data_home
from llobot.utils.zones import Zoning
from llobot.utils.time import current_time

_logger = logging.getLogger(__name__)

class ExampleMemory:
    """
    Manages storage and retrieval of example chats for roles.

    Examples are stored in a ChatArchive and organized into zones based on
    project and role names. This allows roles to retrieve relevant examples
    during context stuffing.
    """
    _role_name: str | None
    _archive: ChatArchive

    def __init__(self,
        role_name: str | None = None,
        *,
        archive: ChatArchive | Zoning | Path | str = standard_chat_archive(data_home()/'llobot/examples'),
    ):
        """
        Initializes the ExampleMemory.

        Args:
            role_name: The name of the role this memory is for.
            archive: The chat archive for storing examples.
        """
        self._role_name = role_name
        self._archive = coerce_chat_archive(archive)

    def _zones(self, env: Environment) -> list[Path]:
        """
        Determines the zone names based on the current environment.
        """
        projects = env[ProjectEnv].selected
        zones: list[Path] = []
        if self._role_name:
            for project in projects:
                zones.append(Path(self._role_name) / project.name)
            zones.append(Path(self._role_name))
        else:
            for project in projects:
                zones.append(Path(project.name))
        return zones

    def save(self, chat: ChatBranch, env: Environment):
        """
        Saves a chat as an example.

        The chat is saved to zones determined by the project and role in the
        environment. Replaces the last example if it has the same prompt.

        Args:
            chat: The chat branch to save.
            env: The environment containing project and other context.

        Raises:
            ValueError: If no zones can be determined for saving.
        """
        zones = self._zones(env)
        if not zones:
            raise ValueError("Cannot save example without a project or role.")

        # Replace the last example if it has the same prompt.
        for zone in zones:
            last_time, last_chat = self._archive.last(zone)
            if last_chat and len(last_chat) > 0 and len(chat) > 0 and last_chat[0].content == chat[0].content:
                self._archive.remove(zone, last_time)

        time = current_time()
        self._archive.scatter(zones, time, chat)
        _logger.info(f"Archived example: {', '.join(map(str, zones))}")

    def _as_example(self, chat: ChatBranch) -> ChatBranch:
        """Converts all messages in a chat branch to their example versions."""
        messages = []
        for message in chat:
            if binarize_intent(message.intent) == ChatIntent.RESPONSE:
                example_intent = ChatIntent.EXAMPLE_RESPONSE
            else:
                example_intent = ChatIntent.EXAMPLE_PROMPT
            messages.append(ChatMessage(example_intent, message.content))
        return ChatBranch(messages)

    def recent(self, env: Environment) -> Iterable[ChatBranch]:
        """
        Retrieves recent examples.

        Examples are retrieved from zones determined by the projects and role in
        the environment. Examples from project-specific zones are merged and
        yielded first in reverse chronological order, followed by examples from
        the role-only zone. Duplicates are removed.

        Args:
            env: The environment containing projects and cutoff time.

        Returns:
            An iterable of recent example chat branches.
        """
        cutoff = env[CutoffEnv].get()
        seen = set()

        all_zones = self._zones(env)
        project_zones = all_zones[:]
        role_zone_iter = []

        if self._role_name:
            role_path = Path(self._role_name)
            if role_path in project_zones:
                project_zones.remove(role_path)
                role_zone_iter = self._archive.recent(role_path, cutoff)

        # Merge examples from all project zones, sorted by time descending.
        project_iters = [self._archive.recent(zone, cutoff) for zone in project_zones]
        merged_project_examples = merge(*project_iters, key=lambda item: item[0], reverse=True)

        all_examples = chain(merged_project_examples, role_zone_iter)

        for _, chat in all_examples:
            if chat not in seen:
                seen.add(chat)
                yield self._as_example(chat)

__all__ = [
    'ExampleMemory',
]
