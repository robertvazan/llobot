"""
Submessage formatting for packing multiple messages into one.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.intents import ChatIntent
from llobot.models.streams import ModelStream

class SubmessageFormat:
    """
    Base class for submessage formats.

    Submessage formats pack a `ChatBranch` into a single string.
    They can also parse the formatted string back into a `ChatBranch`.
    """
    def render(self, chat: ChatBranch) -> str:
        """
        Renders a chat branch into a single string.

        Args:
            chat: The chat branch to render.

        Returns:
            A single string representing the branch.
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

    def parse(self, formatted: str) -> ChatBranch:
        """
        Parses a formatted string back into a chat branch.

        Args:
            formatted: The string to parse.

        Returns:
            A `ChatBranch` object.
        """
        raise NotImplementedError

    def parse_chat(self, chat: ChatBranch) -> ChatBranch:
        """
        Parses submessages within RESPONSE messages of a chat branch.

        Args:
            chat: The chat branch to parse.

        Returns:
            A new `ChatBranch` with submessages expanded.
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
