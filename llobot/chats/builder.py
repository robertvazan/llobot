from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream

class ChatBuilder:
    """
    A mutable builder for constructing ChatThread instances.

    The builder allows for incrementally adding messages or entire threads,
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

    def __getitem__(self, key: int | slice) -> ChatMessage | ChatThread:
        if isinstance(key, slice):
            return ChatThread(self._messages[key])
        return self._messages[key]

    def add(self, what: ChatMessage | ChatThread | None):
        """
        Adds content to the chat.

        - A `ChatThread` adds all its messages.
        - A `ChatMessage` is appended.
        - `None` is ignored.

        Args:
            what: The content to add.
        """
        if isinstance(what, ChatThread):
            for message in what:
                self.add(message)
        elif isinstance(what, ChatMessage):
            self._messages.append(what)
        elif what is None:
            pass
        else:
            raise TypeError(what)

    def record(self, stream: ChatStream) -> ChatStream:
        """
        Records a model stream while passing it through.

        This method iterates over a `ChatStream`, appends the resulting chat
        messages to the builder, and yields the stream's items unchanged. It
        acts as a pass-through that records the conversation. The stream is
        interpreted according to the rules in `llobot.chats.stream`.

        Args:
            stream: The `ChatStream` to record.

        Yields:
            The items from the input stream.
        """
        current_intent: ChatIntent | None = None
        current_content_parts = []

        for item in stream:
            yield item
            if isinstance(item, ChatIntent):
                if current_intent is not None:
                    content = "".join(current_content_parts)
                    self.add(ChatMessage(current_intent, content))
                current_intent = item
                current_content_parts = []
            else:  # str
                current_content_parts.append(item)

        if current_intent is not None:
            content = "".join(current_content_parts)
            self.add(ChatMessage(current_intent, content))

    def build(self) -> ChatThread:
        """Constructs an immutable ChatThread from the current state of the builder."""
        return ChatThread(self._messages)

__all__ = [
    'ChatBuilder',
]
