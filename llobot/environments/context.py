"""
Context environment component for accumulating prompt messages.
"""
from __future__ import annotations
from llobot.chats.builders import ChatBuilder
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage

class ContextEnv:
    """
    An environment component that accumulates messages for the LLM context.
    """
    _builder: ChatBuilder

    def __init__(self):
        self._builder = ChatBuilder()

    @property
    def builder(self) -> ChatBuilder:
        """The internal ChatBuilder instance."""
        return self._builder

    def add(self, what: ChatMessage | ChatBranch | None):
        """Adds content to the context."""
        self._builder.add(what)

    def build(self) -> ChatBranch:
        """Constructs an immutable ChatBranch from the current context."""
        return self._builder.build()

    @property
    def messages(self) -> list[ChatMessage]:
        """A copy of the list of messages currently in the context."""
        return self._builder.messages

    @property
    def cost(self) -> int:
        """The total estimated cost of all messages currently in the context."""
        return self._builder.cost

__all__ = [
    'ContextEnv',
]
