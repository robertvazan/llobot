from __future__ import annotations
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch

class ChatBuilder:
    """
    A mutable builder for constructing ChatBranch instances.

    The builder allows for incrementally adding messages or entire branches,
    and it merges consecutive messages that have the same intent.
    """
    _messages: list[ChatMessage]

    def __init__(self):
        """Initializes an empty ChatBuilder."""
        self._messages = []

    @property
    def messages(self) -> list[ChatMessage]:
        """A copy of the list of messages currently in the builder."""
        return self._messages.copy()

    def __str__(self) -> str:
        return str(self._messages)

    def __bool__(self) -> bool:
        return bool(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    @property
    def cost(self) -> int:
        """The total estimated cost of all messages currently in the builder."""
        return self.build().cost

    def __getitem__(self, key: int | slice) -> ChatMessage | ChatBranch:
        if isinstance(key, slice):
            return ChatBranch(self._messages[key])
        return self._messages[key]

    def add(self, what: ChatIntent | str | ChatMessage | ChatBranch | None):
        """
        Adds content to the chat.

        - A `ChatBranch` adds all its messages.
        - A `ChatMessage` is appended. If its intent matches the last message,
          their content is merged.
        - A `ChatIntent` starts a new, empty message with that intent.
        - A `str` is appended to the content of the last message.
        - `None` is ignored.

        Args:
            what: The content to add.
        """
        if isinstance(what, ChatBranch):
            for message in what:
                self.add(message)
        elif isinstance(what, ChatMessage):
            if self and self[-1].intent == what.intent:
                self._messages[-1] = self[-1].with_postscript(what.content)
            else:
                self._messages.append(what)
        elif isinstance(what, ChatIntent):
            self._messages.append(ChatMessage(what, ''))
        elif isinstance(what, str):
            self._messages[-1] = self[-1].with_postscript(what)
        elif what is None:
            pass
        else:
            raise TypeError(what)

    def prepend(self, what: ChatMessage | ChatBranch | None):
        """
        Prepends messages to the beginning of the chat.

        Unlike `add`, this method does not merge messages.

        Args:
            what: The message or branch to prepend.
        """
        if isinstance(what, ChatBranch):
            self._messages = what.messages + self._messages
        elif isinstance(what, ChatMessage):
            self._messages.insert(0, what)
        elif what is None:
            pass
        else:
            raise TypeError(what)

    def build(self) -> ChatBranch:
        """Constructs an immutable ChatBranch from the current state of the builder."""
        return ChatBranch(self._messages)

__all__ = [
    'ChatBuilder',
]
