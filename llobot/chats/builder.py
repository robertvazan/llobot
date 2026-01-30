from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream

class ChatBuilder:
    """
    A mutable builder for constructing ChatThread instances.

    The builder allows for incrementally adding messages or entire threads.

    It supports speculative appends via `mark()` and `undo()` methods.
    Code that uses these methods is responsible for storing the mark.
    """
    _messages: list[ChatMessage]

    def __init__(self):
        """Initializes an empty ChatBuilder."""
        self._messages = []

    @property
    def messages(self) -> list[ChatMessage]:
        """A copy of the list of messages currently in the builder."""
        return self._messages.copy()

    def remaining(self, mark: int, budget: int) -> int:
        """
        Calculates the remaining budget after accounting for messages added since the mark.

        This method calculates the cost of all messages added after the specified
        mark and subtracts it from the provided budget. The result can be negative
        if the added messages exceed the budget.

        Args:
            mark: The message count from which to start calculating cost.
            budget: The total budget available.

        Returns:
            The remaining budget.

        Raises:
            ValueError: If mark is negative.
        """
        if mark < 0:
            raise ValueError("Mark cannot be negative")
        cost = ChatThread(self._messages[mark:]).cost
        return budget - cost

    def mark(self) -> int:
        """
        Returns the current message count.

        The returned value can be passed to `undo()`, `extension()`, or
        `remaining()` to reference the current state of the builder.

        Returns:
            The index of the marked position.
        """
        return len(self._messages)

    def undo(self, mark: int):
        """
        Restores the builder to a previously marked state.

        Args:
            mark: The message count to revert to.
        """
        if mark < 0:
            raise ValueError("Mark cannot be negative")
        if len(self._messages) > mark:
            self._messages = self._messages[:mark]

    def extension(self, mark: int) -> ChatThread:
        """
        Returns a ChatThread containing messages added since the mark.

        Args:
            mark: The starting position.

        Returns:
            A ChatThread with new messages.
        """
        if mark < 0:
            raise ValueError("Mark cannot be negative")
        return ChatThread(self._messages[mark:])

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
