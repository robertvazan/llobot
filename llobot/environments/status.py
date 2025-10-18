"""
Status messages.
"""
from __future__ import annotations
from llobot.utils.text import concat_documents
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream

class StatusEnv:
    """
    An environment component that accumulates status messages from commands.
    """
    _fragments: list[str]

    def __init__(self):
        self._fragments = []

    def append(self, text: str | None):
        """
        Appends a Markdown fragment to the status message.

        The fragment is ignored if the text is empty.
        """
        if text:
            self._fragments.append(text)

    @property
    def populated(self) -> bool:
        """
        Checks if any status fragments have been added.
        """
        return bool(self._fragments)

    def content(self) -> str:
        """
        Returns the combined content of all status message fragments.
        """
        return concat_documents(*self._fragments)

    def message(self) -> ChatMessage | None:
        """
        Constructs a status message from accumulated fragments.

        Returns:
            A `ChatMessage` with `RESPONSE` intent, or `None` if no fragments were added.
        """
        content = self.content()
        if not content:
            return None
        return ChatMessage(ChatIntent.RESPONSE, content)

    def stream(self) -> ChatStream:
        """
        Constructs a status message and returns it as a stream.

        Returns:
            A `ChatStream` containing the status message, or an empty stream if no
            fragments were added.
        """
        msg = self.message()
        if msg:
            yield from msg.stream()

__all__ = [
    'StatusEnv',
]
