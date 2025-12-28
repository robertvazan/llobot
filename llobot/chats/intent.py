from __future__ import annotations
from enum import Enum

class ChatIntent(Enum):
    """
    Specifies the type and purpose of a chat message.

    This enum provides a fine-grained classification of messages, allowing
    different parts of a conversation to be identified and handled
    appropriately. The role (user or model) can be determined from the intent.

    Attributes:
        SYSTEM: System messages include the system prompt, files from the
            knowledge base, file lists, and other project information. They are
            prepended to the user prompt and are not directly part of the
            conversational history.
        EXAMPLE_PROMPT: The prompt part of a few-shot example. Example
            prompt/response pairs are taken from example archives maintained by
            roles.
        EXAMPLE_RESPONSE: The response part of a few-shot example.
        PROMPT: The user's prompt as seen in the chat front-end. This notably
            excludes any messages automatically inserted by roles.
        RESPONSE: The model's response to a user prompt, as seen in the chat
            front-end.
        STATUS: Role-generated status messages (e.g., confirmations of actions
            taken or error reports), which are given this intent to ensure they
            are prominently displayed in the chat UI.
    """
    SYSTEM = 'System'
    EXAMPLE_PROMPT = 'Example-Prompt'
    EXAMPLE_RESPONSE = 'Example-Response'
    PROMPT = 'Prompt'
    RESPONSE = 'Response'
    STATUS = 'Status'

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
        if codename == 'Example-Prompt':
            return ChatIntent.EXAMPLE_PROMPT
        if codename == 'Example-Response':
            return ChatIntent.EXAMPLE_RESPONSE
        if codename == 'Prompt':
            return ChatIntent.PROMPT
        if codename == 'Response':
            return ChatIntent.RESPONSE
        if codename == 'Status':
            return ChatIntent.STATUS
        raise ValueError(f'Unknown intent: {codename}')

__all__ = [
    'ChatIntent',
]
