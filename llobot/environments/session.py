"""
Session messages.
"""
from __future__ import annotations
from datetime import datetime
from llobot.utils.text import concat_documents
from llobot.utils.time import format_time
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream

class SessionEnv:
    """
    An environment component that accumulates session messages from commands
    and holds the session ID.
    """
    _fragments: list[str]
    _id: datetime | None

    def __init__(self):
        self._fragments = []
        self._id = None

    def set_id(self, session_id: datetime):
        """
        Sets the session ID for the environment.

        It is okay to set the same session ID multiple times.

        Args:
            session_id: The session ID to set.

        Raises:
            ValueError: If a different session ID is already set.
        """
        if self._id is not None and self._id != session_id:
            raise ValueError(f"Session ID already set to {format_time(self._id)}, cannot change to {format_time(session_id)}")
        self._id = session_id

    def get_id(self) -> datetime | None:
        """
        Gets the currently configured session ID.

        Returns:
            The configured session ID, or None if not set.
        """
        return self._id

    def append(self, text: str | None):
        """
        Appends a Markdown fragment to the session message.

        The fragment is ignored if the text is empty.
        """
        if text:
            self._fragments.append(text)

    @property
    def populated(self) -> bool:
        """
        Checks if any session fragments have been added.
        """
        return bool(self._fragments)

    def content(self) -> str:
        """
        Returns the combined content of all session message fragments.
        """
        return concat_documents(*self._fragments)

    def message(self) -> ChatMessage | None:
        """
        Constructs a session message from accumulated fragments.

        Returns:
            A `ChatMessage` with `SESSION` intent, or `None` if no fragments were added.
        """
        content = self.content()
        if not content:
            return None
        return ChatMessage(ChatIntent.SESSION, content)

    def stream(self) -> ChatStream:
        """
        Constructs a session message and returns it as a stream.

        Returns:
            A `ChatStream` containing the session message, or an empty stream if no
            fragments were added.
        """
        msg = self.message()
        if msg:
            yield from msg.stream()

__all__ = [
    'SessionEnv',
]
