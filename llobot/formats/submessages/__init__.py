"""
Submessage formatting for packing multiple messages into one.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.models.streams import ModelStream

class SubmessageFormat:
    """
    Base class for submessage formats.

    Submessage formats pack a `ChatThread` into a single string.
    They can also parse the formatted string back into a `ChatThread`.
    """
    def render(self, chat: ChatThread) -> str:
        """
        Renders a chat thread into a single string.

        Args:
            chat: The chat thread to render.

        Returns:
            A single string representing the thread.
        """
        raise NotImplementedError

    def render_stream(self, stream: ModelStream) -> ModelStream:
        """
        Renders a model stream into a single message stream.

        Args:
            stream: The model stream to format.

        Returns:
            A new stream of strings containing the formatted output.
        """
        raise NotImplementedError

    def parse(self, formatted: str) -> ChatThread:
        """
        Parses a formatted string back into a chat thread.

        Args:
            formatted: The string to parse.

        Returns:
            A `ChatThread` object.
        """
        raise NotImplementedError

    def parse_chat(self, chat: ChatThread) -> ChatThread:
        """
        Parses submessages within RESPONSE messages of a chat thread.

        Args:
            chat: The chat thread to parse.

        Returns:
            A new `ChatThread` with submessages expanded.
        """
        builder = ChatBuilder()
        for message in chat:
            if message.intent == ChatIntent.RESPONSE:
                builder.add(self.parse(message.content))
            else:
                builder.add(message)
        return builder.build()

def standard_submessage_format() -> SubmessageFormat:
    """
    Returns the standard submessage format.

    Returns:
        The standard `SubmessageFormat`.
    """
    from llobot.formats.submessages.details import DetailsSubmessageFormat
    return DetailsSubmessageFormat()

__all__ = [
    'SubmessageFormat',
    'standard_submessage_format',
]
