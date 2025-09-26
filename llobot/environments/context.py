from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.messages import ChatMessage

class ContextEnv:
    """
    An environment component for accumulating chat messages.
    """
    _builder: ChatBuilder

    def __init__(self):
        self._builder = ChatBuilder()

    @property
    def messages(self) -> list[ChatMessage]:
        """
        A copy of the list of messages currently in the context.
        """
        return self._builder.messages

    @property
    def populated(self) -> bool:
        """
        Checks if any messages have been added to the context.
        """
        return bool(self._builder)

    @property
    def builder(self) -> ChatBuilder:
        """
        The underlying `ChatBuilder` for this context.
        """
        return self._builder

    def add(self, branch: ChatBranch | ChatMessage | None):
        """
        Adds messages to the context.
        """
        self._builder.add(branch)

    def build(self) -> ChatBranch:
        """
        Builds the final `ChatBranch` from the accumulated messages.
        """
        return self._builder.build()

__all__ = [
    'ContextEnv',
]
