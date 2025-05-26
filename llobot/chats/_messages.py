from __future__ import annotations
from ._roles import ChatRole
from ._intents import ChatIntent

# Guesstimate of how many chars are consumed per message by typical chat format.
MESSAGE_OVERHEAD: int = 10

class ChatMessage:
    _intent: ChatIntent
    _content: str

    def __init__(self, kind: ChatRole | ChatIntent, content: str):
        if isinstance(kind, ChatRole):
            self._intent = kind.intent
        elif isinstance(kind, ChatIntent):
            self._intent = kind
        else:
            raise TypeError
        self._content = content

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
        return hash((self.intent, self.content))

    def __contains__(self, text: str) -> bool:
        return text in self.content
    
    def branch(self) -> 'ChatBranch':
        from ._branches import ChatBranch
        return ChatBranch([self])
    
    def with_intent(self, intent: ChatIntent) -> ChatMessage:
        return intent.message(self.content)
    
    def as_example(self) -> ChatMessage:
        return self.with_intent(self.intent.as_example())
    
    def is_example(self) -> bool:
        return self.intent.is_example()

    def monolithic(self) -> str:
        return f'**{self.intent}:**\n\n{self.content}'
    
    def with_content(self, content: str) -> ChatMessage:
        return ChatMessage(self.intent, content)

    def with_postscript(self, postscript: str) -> ChatMessage:
        return self.with_content((self.content.strip() + '\n\n' + postscript.strip()).strip())

