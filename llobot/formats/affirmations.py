"""
Utilities for creating affirmation messages.
"""
from __future__ import annotations
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder

def affirmation_text() -> str:
    """Returns the standard affirmation text."""
    return "Okay"

def affirmation_message() -> ChatMessage:
    """Returns a standard affirmation message."""
    return ChatMessage(ChatIntent.AFFIRMATION, affirmation_text())

def affirmation_turn(message: ChatMessage) -> ChatBranch:
    """Creates a chat branch with a message followed by an affirmation."""
    builder = ChatBuilder()
    builder.add(message)
    builder.add(affirmation_message())
    return builder.build()

__all__ = [
    'affirmation_text',
    'affirmation_message',
    'affirmation_turn',
]
