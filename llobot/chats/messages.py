from __future__ import annotations
from llobot.text import concat_documents
from llobot.chats.intents import ChatIntent

# Guesstimate of how many chars are consumed per message by typical chat format.
MESSAGE_OVERHEAD: int = 10

class ChatMessage:
    """
    Represents a single message in a chat conversation.

    A message consists of an intent and content. It is immutable.
    """
    _intent: ChatIntent
    _content: str
    _hash: int | None

    def __init__(self, intent: ChatIntent, content: str):
        """
        Initializes a new ChatMessage.

        Args:
            intent: The intent of the message.
            content: The text content of the message.
        """
        self._intent = intent
        self._content = content
        self._hash = None

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

    def __eq__(self, other) -> bool:
        if not isinstance(other, ChatMessage):
            return NotImplemented
        return self.intent == other.intent and self.content == other.content

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((self.intent, self.content))
        return self._hash

    def __contains__(self, text: str) -> bool:
        return text in self.content

    def branch(self) -> 'ChatBranch':
        """Converts this message into a ChatBranch containing only this message."""
        from llobot.chats.branches import ChatBranch
        return ChatBranch([self])

    def with_intent(self, intent: ChatIntent) -> ChatMessage:
        """Creates a new message with the same content but a different intent."""
        return ChatMessage(intent, self.content)

    def as_example(self) -> ChatMessage:
        """Converts this message to its corresponding example version."""
        return self.with_intent(self.intent.as_example())

    def monolithic(self) -> str:
        """
        Returns a single-string representation of the message, including its intent.
        """
        return concat_documents(f'**{self.intent}:**', self.content)

    def with_content(self, content: str) -> ChatMessage:
        """Creates a new message with the same intent but different content."""
        return ChatMessage(self.intent, content)

    def with_postscript(self, postscript: str) -> ChatMessage:
        """
        Appends a postscript to the message content.

        If the message has no content, the postscript becomes the content.
        Otherwise, it's appended after a double newline.
        """
        if not postscript:
            return self
        if not self.content:
            return self.with_content(postscript)
        return self.with_content(concat_documents(self.content, postscript))

__all__ = [
    'ChatMessage',
    'MESSAGE_OVERHEAD',
]
