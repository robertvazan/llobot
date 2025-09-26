from __future__ import annotations
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch

class ChatBuilder:
    """
    A mutable builder for constructing ChatBranch instances.

    The builder allows for incrementally adding messages or entire branches,
    and it merges consecutive messages that have the same intent.

    It supports a budget for content size, and speculative appends via `mark()`
    and `undo()` methods.
    """
    _messages: list[ChatMessage]
    _budget: int
    _mark: int

    def __init__(self):
        """Initializes an empty ChatBuilder."""
        self._messages = []
        self._budget = 0
        self._mark = 0

    @property
    def messages(self) -> list[ChatMessage]:
        """A copy of the list of messages currently in the builder."""
        return self._messages.copy()

    @property
    def budget(self) -> int:
        """
        The total character budget for the chat. Defaults to zero (unlimited).
        """
        return self._budget

    @budget.setter
    def budget(self, value: int):
        self._budget = value

    @property
    def unused(self) -> int:
        """
        The remaining characters in the budget. Can be negative if over budget.
        """
        return self._budget - self.cost

    def mark(self):
        """
        Saves the current state of the builder.

        A subsequent call to `undo()` with no arguments will restore the builder
        to this state.
        """
        self._mark = len(self._messages)

    def undo(self, mark: int | None = None):
        """
        Restores the builder to a previously marked state.

        Args:
            mark: The message count to revert to. If `None`, reverts to the
                  last position saved by `mark()`.
        """
        target_len = mark if mark is not None else self._mark
        if len(self._messages) > target_len:
            self._messages = self._messages[:target_len]

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

    def add(self, what: ChatMessage | ChatBranch | None):
        """
        Adds content to the chat.

        - A `ChatBranch` adds all its messages.
        - A `ChatMessage` is appended.
        - `None` is ignored.

        Args:
            what: The content to add.
        """
        if isinstance(what, ChatBranch):
            for message in what:
                self.add(message)
        elif isinstance(what, ChatMessage):
            self._messages.append(what)
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
