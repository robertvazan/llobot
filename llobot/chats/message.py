from __future__ import annotations
from llobot.utils.values import ValueTypeMixin
from llobot.chats.intent import ChatIntent

# Guesstimate of how many chars are consumed per message by typical chat format.
MESSAGE_OVERHEAD: int = 10

class ChatMessage(ValueTypeMixin):
    """
    Represents a single message in a chat conversation.

    A message consists of an intent and content. It is immutable.
    """
    _intent: ChatIntent
    _content: str

    def __init__(self, intent: ChatIntent, content: str):
        """
        Initializes a new ChatMessage.

        Args:
            intent: The intent of the message.
            content: The text content of the message.
        """
        self._intent = intent
        self._content = content

    @property
    def intent(self) -> ChatIntent:
        """The intent of the message."""
        return self._intent

    @property
    def content(self) -> str:
        """The text content of the message."""
        return self._content

    @property
    def cost(self) -> int:
        """Estimated cost of the message in characters, including overhead."""
        return len(self.content) + MESSAGE_OVERHEAD

    def __repr__(self) -> str:
        return f'{self.intent}: {self.content}'

    def __contains__(self, text: str) -> bool:
        return text in self.content

__all__ = [
    'ChatMessage',
    'MESSAGE_OVERHEAD',
]
