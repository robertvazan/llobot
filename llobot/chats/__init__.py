"""
Data structures for representing chat conversations.

This package provides classes for representing chat messages, threads of conversation,
and builders for constructing them. It also includes utilities for binarizing
chats into a strict prompt/response sequence.

Submodules
----------
intent
    Defines `ChatIntent` for message types.
message
    Defines `ChatMessage` for individual messages.
thread
    Defines `ChatThread` for sequences of messages.
builder
    Defines `ChatBuilder` for constructing chats.
binarization
    Provides functions for chat binarization.
history
    Manages storage of chat histories.
markdown
    An implementation of `ChatHistory` that stores chats as Markdown files.
monolithic
    Functions to get single-string representation of chats.
"""
