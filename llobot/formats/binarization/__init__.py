"""
Formats for normalizing chats into strict prompt/response sequences.

This package provides the `BinarizationFormat` interface and its implementations.
Binarization converts a chat thread with various message intents (SYSTEM,
STATUS, etc.) into a sequence of strictly alternating PROMPT and RESPONSE
messages, which is required by most LLM APIs.

Submodules
----------
separator
    A binarization format that merges consecutive messages of the same group.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread

class BinarizationFormat:
    """
    Interface for chat binarization formats.
    """
    def binarize_intent(self, intent: ChatIntent) -> ChatIntent:
        """
        Maps a generic chat intent to either PROMPT or RESPONSE.
        """
        raise NotImplementedError

    def binarize_message(self, message: ChatMessage) -> ChatMessage:
        """
        Converts a message to a binarized PROMPT or RESPONSE message.
        """
        return ChatMessage(self.binarize_intent(message.intent), message.content)

    def binarize_chat(self, chat: ChatThread) -> ChatThread:
        """
        Normalizes a chat thread into a sequence of PROMPT/RESPONSE messages.
        """
        raise NotImplementedError

def standard_binarization_format() -> BinarizationFormat:
    """
    Returns the standard binarization format.
    """
    from llobot.formats.binarization.separator import SeparatorBinarizationFormat
    return SeparatorBinarizationFormat()

__all__ = [
    'BinarizationFormat',
    'standard_binarization_format',
]
