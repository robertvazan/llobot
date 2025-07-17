from __future__ import annotations
from enum import Enum

class ChatRole(Enum):
    USER = 'User'
    MODEL = 'Model'
    
    @property
    def intent(self) -> 'ChatIntent':
        from ._intents import ChatIntent
        if self == ChatRole.USER:
            return ChatIntent.PROMPT
        if self == ChatRole.MODEL:
            return ChatIntent.RESPONSE
        raise ValueError
    
    def __str__(self) -> str:
        return self.value

    def message(self, content: str) -> 'ChatMessage':
        from ._messages import ChatMessage
        return ChatMessage(self, content)

