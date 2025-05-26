from __future__ import annotations
from enum import Enum
from ._roles import ChatRole

# Fine-grained message type, so that we can recognize different parts of the conversation.
# Role can be always determined automatically from intent.
class ChatIntent(Enum):
    # System messages include everything prepended to user prompt, whether static content or prompt-dependent retrievals.
    # The only exception is few-shot examples, which have their own intent types.
    SYSTEM = 'System'
    AFFIRMATION = 'Affirmation'
    EXAMPLE_PROMPT = 'Example-Prompt'
    EXAMPLE_RESPONSE = 'Example-Response'
    # This is the actual user prompt we recevied or one of the followup prompts.
    PROMPT = 'Prompt'
    # This is assistant's response to user prompt, includes followup responses.
    RESPONSE = 'Response'
    
    def __str__(self) -> str:
        return self.value

    @property
    def role(self) -> ChatRole:
        if self == self.SYSTEM:
            return ChatRole.USER
        if self == self.AFFIRMATION:
            return ChatRole.ASSISTANT
        if self == self.EXAMPLE_PROMPT:
            return ChatRole.USER
        if self == self.EXAMPLE_RESPONSE:
            return ChatRole.ASSISTANT
        if self == self.PROMPT:
            return ChatRole.USER
        if self == self.RESPONSE:
            return ChatRole.ASSISTANT
        raise ValueError

    def as_example(self) -> ChatIntent:
        if self == self.PROMPT:
            return self.EXAMPLE_PROMPT
        if self == self.RESPONSE:
            return self.EXAMPLE_RESPONSE
        return self

    def is_example(self) -> bool:
        return self in [self.EXAMPLE_PROMPT, self.EXAMPLE_RESPONSE]

    def message(self, content: str) -> 'ChatMessage':
        from ._messages import ChatMessage
        return ChatMessage(self, content)

