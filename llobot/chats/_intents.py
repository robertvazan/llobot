from __future__ import annotations
from enum import Enum

# Fine-grained message type, so that we can recognize different parts of the conversation.
# Role can be always determined automatically from intent.
class ChatIntent(Enum):
    # System messages include everything prepended to user prompt, whether static content or prompt-dependent retrievals.
    # The only exception is few-shot examples, which have their own intent types.
    SYSTEM = 'System'
    SESSION = 'Session'
    AFFIRMATION = 'Affirmation'
    EXAMPLE_PROMPT = 'Example-Prompt'
    EXAMPLE_RESPONSE = 'Example-Response'
    # This is the actual user prompt we recevied or one of the followup prompts.
    PROMPT = 'Prompt'
    # This is model response to user prompt, includes followup responses.
    RESPONSE = 'Response'

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def parse(codename: str) -> ChatIntent:
        """
        Parses intent from its string representation.

        This is the reverse of `str(intent)`.
        """
        if codename == 'System':
            return ChatIntent.SYSTEM
        if codename == 'Session':
            return ChatIntent.SESSION
        if codename == 'Affirmation':
            return ChatIntent.AFFIRMATION
        if codename == 'Example-Prompt':
            return ChatIntent.EXAMPLE_PROMPT
        if codename == 'Example-Response':
            return ChatIntent.EXAMPLE_RESPONSE
        if codename == 'Prompt':
            return ChatIntent.PROMPT
        if codename == 'Response':
            return ChatIntent.RESPONSE
        raise ValueError(f'Unknown intent: {codename}')

    def binarize(self) -> ChatIntent:
        """
        Reduces the intent to either PROMPT or RESPONSE.
        """
        if self in [self.SYSTEM, self.SESSION, self.EXAMPLE_PROMPT, self.PROMPT]:
            return ChatIntent.PROMPT
        if self in [self.AFFIRMATION, self.EXAMPLE_RESPONSE, self.RESPONSE]:
            return ChatIntent.RESPONSE
        raise ValueError

    def as_example(self) -> ChatIntent:
        if self.binarize() == ChatIntent.RESPONSE:
            return self.EXAMPLE_RESPONSE
        else:
            return self.EXAMPLE_PROMPT
