from __future__ import annotations
from enum import Enum

# Fine-grained message type, so that we can recognize different parts of the conversation.
# Role can be always determined automatically from intent.
class ChatIntent(Enum):
    """
    Specifies the type and purpose of a chat message.

    This enum provides a fine-grained classification of messages, allowing different
    parts of a conversation to be identified and handled appropriately.
    """
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

    def as_example(self) -> ChatIntent:
        """
        Converts this intent to its corresponding example intent.

        Prompt-like intents are converted to `EXAMPLE_PROMPT`, and response-like
        intents are converted to `EXAMPLE_RESPONSE`.

        Returns:
            The example version of the intent.
        """
        import llobot.chats.binarization
        if llobot.chats.binarization.binarize_intent(self) == ChatIntent.RESPONSE:
            return ChatIntent.EXAMPLE_RESPONSE
        else:
            return ChatIntent.EXAMPLE_PROMPT

__all__ = [
    'ChatIntent',
]
