"""
Session messages.
"""
from __future__ import annotations
import llobot.text
from llobot.chats import ChatIntent, ChatMessage
from llobot.environments import EnvBase
from llobot.models.streams import ModelStream
import llobot.models.streams

class SessionEnv(EnvBase):
    """
    An environment component that accumulates session messages from commands.
    """
    _fragments: list[str]
    _recording: bool

    def __init__(self):
        super().__init__()
        self._fragments = []
        self._recording = False

    def append(self, text: str | None):
        """
        Appends a Markdown fragment to the session message.

        The fragment is ignored if recording is off or if the text is empty.
        """
        if self._recording and text:
            self._fragments.append(text)

    def content(self) -> str:
        """
        Returns the combined content of all session message fragments.
        """
        return llobot.text.concat(*self._fragments)

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
            yield from llobot.models.streams.message(msg)

    def recording(self) -> bool:
        """
        Checks whether session data is being recorded.
        """
        return self._recording

    def record(self):
        """
        Turns on recording of session data.
        """
        self._recording = True

__all__ = [
    'SessionEnv',
]
