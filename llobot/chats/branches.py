from __future__ import annotations
from typing import Iterator, Iterable
from llobot.utils.text import concat_documents
from llobot.utils.values import ValueTypeMixin
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage

class ChatBranch(ValueTypeMixin):
    """
    Represents an immutable sequence of chat messages.

    A ChatBranch is a list-like object that holds ChatMessage instances. It provides
    methods for accessing, combining, and transforming branches.
    """
    _messages: tuple[ChatMessage, ...]

    def __init__(self, messages: Iterable[ChatMessage] = []):
        """
        Initializes a new ChatBranch.

        Args:
            messages: An iterable of ChatMessage objects.
        """
        self._messages = tuple(messages)

    @property
    def messages(self) -> tuple[ChatMessage, ...]:
        """The tuple of messages in this branch."""
        return self._messages

    def __repr__(self) -> str:
        return str(self._messages)

    def __bool__(self) -> bool:
        return bool(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    @property
    def cost(self) -> int:
        """The total estimated cost of all messages in the branch."""
        return sum([message.cost for message in self], 0)

    def __getitem__(self, key: int | slice) -> ChatMessage | ChatBranch:
        if isinstance(key, slice):
            return ChatBranch(self._messages[key])
        return self._messages[key]

    def __iter__(self) -> Iterator[ChatMessage]:
        return iter(self._messages)

    def __contains__(self, text: str) -> bool:
        return any((text in message.content) for message in self)

    def __add__(self, suffix: ChatBranch | ChatMessage | None) -> ChatBranch:
        """
        Concatenates this branch with another branch or a single message.
        """
        if suffix is None:
            return self
        if isinstance(suffix, ChatMessage):
            suffix = ChatBranch([suffix])
        return ChatBranch(self._messages + suffix._messages)

    def to_builder(self) -> 'ChatBuilder':
        """Creates a ChatBuilder initialized with the messages from this branch."""
        from llobot.chats.builders import ChatBuilder
        builder = ChatBuilder()
        builder.add(self)
        return builder

    def monolithic(self) -> str:
        """
        Returns a single-string representation of the entire branch.
        """
        return concat_documents(*(message.monolithic() for message in self))

    def __and__(self, other: ChatBranch) -> ChatBranch:
        """
        Finds the common prefix between this branch and another.
        """
        from llobot.chats.builders import ChatBuilder
        shared = ChatBuilder()
        for message1, message2 in zip(self, other):
            if message1 == message2:
                shared.add(message1)
            else:
                break
        return shared.build()

__all__ = [
    'ChatBranch',
]
