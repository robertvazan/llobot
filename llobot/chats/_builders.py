from __future__ import annotations
from ._intents import ChatIntent
from ._messages import ChatMessage
from ._branches import ChatBranch

class ChatBuilder:
    _messages: list[ChatMessage]

    def __init__(self):
        self._messages = []

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
        return self.build().cost

    def __getitem__(self, key: int | slice) -> ChatMessage | ChatBranch:
        if isinstance(key, slice):
            return ChatBranch(self._messages[key])
        return self._messages[key]

    def add(self, what: ChatIntent | str | ChatMessage | ChatBranch | None):
        if isinstance(what, ChatBranch):
            for message in what:
                self.add(message)
        elif isinstance(what, ChatMessage):
            if self and self[-1].intent == what.intent:
                self._messages[-1] = self[-1].with_postscript(what.content)
            else:
                self._messages.append(what)
        elif isinstance(what, ChatIntent):
            self._messages.append(what.message(''))
        elif isinstance(what, str):
            self._messages[-1] = self[-1].with_postscript(what)
        elif what is None:
            pass
        else:
            raise TypeError(what)

    def prepend(self, what: ChatMessage | ChatBranch | None):
        if isinstance(what, ChatBranch):
            self._messages = what.messages + self._messages
        elif isinstance(what, ChatMessage):
            self._messages.insert(0, what)
        elif what is None:
            pass
        else:
            raise TypeError(what)

    def build(self) -> ChatBranch:
        return ChatBranch(self._messages)
