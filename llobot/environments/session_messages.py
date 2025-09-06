"""
Session messages.
"""
from __future__ import annotations
from llobot.text import concat_documents
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.models.streams import ModelStream, message_stream

class SessionMessageEnv:
    """
    An environment component that accumulates session messages from commands.
    """
    _fragments: list[str]

    def __init__(self):
        self._fragments = []

    def append(self, text: str | None):
        """
        Appends a Markdown fragment to the session message.

        The fragment is ignored if the text is empty.
        """
        if text:
            self._fragments.append(text)

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

    def stream(self) -> ModelStream:
        """
        Constructs a session message and returns it as a stream.

        Returns:
            A `ModelStream` containing the session message, or an empty stream if no
            fragments were added.
        """
        msg = self.message()
        if msg:
            yield from message_stream(msg)

__all__ = [
    'SessionMessageEnv',
]
