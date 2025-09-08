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
        SESSION: Session messages are appended to processed prompt messages to
            record session information captured during prompt processing, such as
            the knowledge cutoff time. Models see session messages prepended to
            the user's prompt, so that the user's prompt is immediately followed
            by the model's response in the final context.
        AFFIRMATION: Short, generic responses like "Okay" or "I see." They are
            inserted after system messages to maintain the user-model turn-taking
            sequence when there are several consecutive system messages.
        EXAMPLE_PROMPT: The prompt part of a few-shot example. Example
            prompt/response pairs are taken from example archives maintained by
            roles.
        EXAMPLE_RESPONSE: The response part of a few-shot example.
        PROMPT: The user's prompt as seen in the chat front-end. This notably
            excludes any messages automatically inserted by roles.
        RESPONSE: The model's response to a user prompt, as seen in the chat
            front-end. This also includes role-generated status messages (e.g.,
            confirmations of actions taken), which are given this intent to
            ensure they are prominently displayed in the chat UI.
    """
    SYSTEM = 'System'
    SESSION = 'Session'
    AFFIRMATION = 'Affirmation'
    EXAMPLE_PROMPT = 'Example-Prompt'
    EXAMPLE_RESPONSE = 'Example-Response'
    PROMPT = 'Prompt'
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

__all__ = [
    'ChatIntent',
]
