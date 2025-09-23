"""
Utilities for creating affirmation messages.
"""
from __future__ import annotations
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder

def affirmation_text() -> str:
    """
    Returns the standard affirmation text.

    Returns:
        The standard affirmation text ("Okay").
    """
    return "Okay"

def affirmation_message() -> ChatMessage:
    """
    Returns a standard affirmation message.

    Returns:
        A `ChatMessage` with affirmation intent and standard text.
    """
    return ChatMessage(ChatIntent.AFFIRMATION, affirmation_text())

def affirmation_turn(message: ChatMessage | str) -> ChatBranch:
    """
    Creates a chat branch with a message followed by an affirmation.

    If a string is provided, it's wrapped in a `ChatMessage` with `SYSTEM`
    intent. If the string is empty or whitespace-only, an empty branch
    is returned.

    Args:
        message: The message to include, as a `ChatMessage` or a string.

    Returns:
        A `ChatBranch` containing the message and a following affirmation, or an
        empty branch if the input message string is empty.
    """
    if isinstance(message, str):
        message = message.strip()
        if not message:
            return ChatBranch()
        message = ChatMessage(ChatIntent.SYSTEM, message)
    builder = ChatBuilder()
    builder.add(message)
    builder.add(affirmation_message())
    return builder.build()

__all__ = [
    'affirmation_text',
    'affirmation_message',
    'affirmation_turn',
]
