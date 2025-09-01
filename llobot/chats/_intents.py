from __future__ import annotations
from enum import Enum

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
    # This is model response to user prompt, includes followup responses.
    RESPONSE = 'Response'

    def __str__(self) -> str:
        return self.value

    def binarize(self) -> ChatIntent:
        """
        Reduces the intent to either PROMPT or RESPONSE.
        """
        if self in [self.SYSTEM, self.EXAMPLE_PROMPT, self.PROMPT]:
            return ChatIntent.PROMPT
        if self in [self.AFFIRMATION, self.EXAMPLE_RESPONSE, self.RESPONSE]:
            return ChatIntent.RESPONSE
        raise ValueError

    def as_example(self) -> ChatIntent:
        if self.binarize() == ChatIntent.RESPONSE:
            return self.EXAMPLE_RESPONSE
        else:
            return self.EXAMPLE_PROMPT
