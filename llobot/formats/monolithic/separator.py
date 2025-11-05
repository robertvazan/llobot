"""
Separator-based monolithic format.
"""
from __future__ import annotations
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.formats.monolithic import MonolithicFormat
from llobot.utils.values import ValueTypeMixin

class SeparatorMonolithicFormat(MonolithicFormat, ValueTypeMixin):
    """
    A monolithic format that joins messages with a separator.

    Message intents are not included in the output. A horizontal ruler
    is used as a separator between messages.
    """
    _separator: str

    def __init__(self, separator: str = '\n\n---\n\n'):
        """
        Initializes the separator-based format.

        Args:
            separator: The string to use as a separator between messages.
        """
        self._separator = separator

    def render(self, chat: ChatThread) -> str:
        """
        Renders a chat by joining the content of its messages with a separator.

        Empty messages are filtered out.

        Args:
            chat: The chat thread to render.

        Returns:
            A single string with all message contents joined by the separator.
        """
        return self._separator.join([
            message.content
            for message in chat
            if message.content and message.content.strip()
        ])

__all__ = [
    'SeparatorMonolithicFormat',
]
