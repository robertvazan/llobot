"""
Data structures for representing chat conversations.

This package provides classes for representing chat messages, branches of conversation,
and builders for constructing them. It also includes utilities for binarizing
chats into a strict prompt/response sequence.

Subpackages
-----------
archives
    Manages storage of chat histories.

Submodules
----------
intents
    Defines `ChatIntent` for message types.
messages
    Defines `ChatMessage` for individual messages.
branches
    Defines `ChatBranch` for sequences of messages.
builders
    Defines `ChatBuilder` for constructing chats.
binarization
    Provides functions for chat binarization.
"""
