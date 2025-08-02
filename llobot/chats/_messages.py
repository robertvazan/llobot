from __future__ import annotations
import llobot.text
from ._roles import ChatRole
from ._intents import ChatIntent

# Guesstimate of how many chars are consumed per message by typical chat format.
MESSAGE_OVERHEAD: int = 10

class ChatMessage:
    _intent: ChatIntent
    _content: str
    _hash: int | None

    def __init__(self, kind: ChatRole | ChatIntent, content: str):
        if isinstance(kind, ChatRole):
            self._intent = kind.intent
        elif isinstance(kind, ChatIntent):
            self._intent = kind
        else:
            raise TypeError
        self._content = content
        self._hash = None

    @property
    def role(self) -> ChatRole:
        return self.intent.role

    @property
    def intent(self) -> ChatIntent:
        return self._intent

    @property
    def content(self) -> str:
        return self._content

    @property
    def cost(self) -> int:
        return len(self.content) + MESSAGE_OVERHEAD

    def __str__(self) -> str:
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
        from ._branches import ChatBranch
        return ChatBranch([self])

    def with_intent(self, intent: ChatIntent) -> ChatMessage:
        return intent.message(self.content)

    def as_example(self) -> ChatMessage:
        return self.with_intent(self.intent.as_example())

    def monolithic(self) -> str:
        return llobot.text.concat(f'**{self.intent}:**', self.content)

    def with_content(self, content: str) -> ChatMessage:
        return ChatMessage(self.intent, content)

    def with_postscript(self, postscript: str) -> ChatMessage:
        if not postscript:
            return self
        if not self.content:
            return self.with_content(postscript)
        return self.with_content(llobot.text.concat(self.content, postscript))
