from __future__ import annotations
import llobot.text
from ._intents import ChatIntent
from ._messages import ChatMessage

class ChatBranch:
    _messages: list[ChatMessage]

    def __init__(self, messages: list[ChatMessage] = []):
        self._messages = messages

    @property
    def messages(self) -> list[ChatMessage]:
        return self._messages.copy()

    def __str__(self) -> str:
        return str(self._messages)

    def __bool__(self) -> bool:
        return bool(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    @property
    def cost(self) -> int:
        return sum([message.cost for message in self], 0)

    @property
    def pretty_cost(self) -> str:
        cost = self.cost
        kb = cost / 1000
        if kb < 10:
            return f"{kb:.1f} KB"
        return f"{kb:.0f} KB"

    def __getitem__(self, key: int | slice) -> ChatMessage | ChatBranch:
        if isinstance(key, slice):
            return ChatBranch(self._messages[key])
        return self._messages[key]

    def __iter__(self) -> Iterator[ChatMessage]:
        return iter(self._messages)

    def __contains__(self, text: str) -> bool:
        return any((text in message.content) for message in self)

    def __add__(self, suffix: ChatBranch | ChatMessage | None) -> ChatBranch:
        if suffix is None:
            return self
        if isinstance(suffix, ChatMessage):
            suffix = suffix.branch()
        return ChatBranch(self._messages + suffix._messages)

    def to_builder(self) -> 'ChatBuilder':
        from ._builders import ChatBuilder
        builder = ChatBuilder()
        builder.add(self)
        return builder

    def as_example(self) -> ChatBranch:
        return ChatBranch([message.as_example() for message in self])

    def monolithic(self) -> str:
        return llobot.text.concat(*(message.monolithic() for message in self))

    def __and__(self, other: ChatBranch) -> ChatBranch:
        from ._builders import ChatBuilder
        shared = ChatBuilder()
        for message1, message2 in zip(self, other):
            if message1 == message2:
                shared.add(message1)
            else:
                break
        return shared.build()
