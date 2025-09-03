"""
Data structures for representing chat conversations.

This package provides classes for representing chat messages, branches of conversation,
and builders for constructing them. It also includes utilities for binarizing
chats into a strict prompt/response sequence.

Submodules
----------
_intents
    Defines `ChatIntent` for message types.
_messages
    Defines `ChatMessage` for individual messages.
_branches
    Defines `ChatBranch` for sequences of messages.
_builders
    Defines `ChatBuilder` for constructing chats.
binarization
    Provides functions for chat binarization.
archives
    Manages storage of chat histories.
markdown
    Handles serialization of chats to/from Markdown format.
"""
from ._intents import ChatIntent
from ._messages import ChatMessage
from ._branches import ChatBranch
from ._builders import ChatBuilder

__all__ = [
    'ChatIntent',
    'ChatMessage',
    'ChatBranch',
    'ChatBuilder'
]
