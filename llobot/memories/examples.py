from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.chats.archives import ChatArchive, standard_chat_archive, coerce_chat_archive
from llobot.chats.binarization import binarize_intent
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.fs import data_home
from llobot.fs.zones import Zoning
from llobot.time import current_time

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

    def _zones(self, env: Environment) -> list[str]:
        """
        Determines the zone names based on the current environment.
        """
        project = env[ProjectEnv].get()
        zones = []
        if self._role_name:
            if project:
                zones.append(f'{project.name}-{self._role_name}')
            zones.append(self._role_name)
        elif project:
            zones.append(project.name)
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
        _logger.info(f"Archived example: {', '.join(zones)}")

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

        Examples are retrieved from zones determined by the project and role in
        the environment.

        Args:
            env: The environment containing project and cutoff time.

        Returns:
            An iterable of recent example chat branches.
        """
        cutoff = env[CutoffEnv].get()
        for zone in self._zones(env):
            for time, chat in self._archive.recent(zone, cutoff):
                yield self._as_example(chat)

__all__ = [
    'ExampleMemory',
]
