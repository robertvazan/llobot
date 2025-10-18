"""
Utilities for creating affirmation messages.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder

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

def affirmation_turn(message: ChatMessage | str) -> ChatThread:
    """
    Creates a chat thread with a message followed by an affirmation.

    If a string is provided, it's wrapped in a `ChatMessage` with `SYSTEM`
    intent. If the string is empty or whitespace-only, an empty thread
    is returned.

    Args:
        message: The message to include, as a `ChatMessage` or a string.

    Returns:
        A `ChatThread` containing the message and a following affirmation, or an
        empty thread if the input message string is empty.
    """
    if isinstance(message, str):
        message = message.strip()
        if not message:
            return ChatThread()
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
