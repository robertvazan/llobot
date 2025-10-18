"""
Functions to get single-string representation of chats.
"""
from __future__ import annotations
from llobot.utils.text import concat_documents
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread

def monolithic_message(message: ChatMessage) -> str:
    """
    Returns a single-string representation of the message, including its intent.
    """
    return concat_documents(f'**{message.intent}:**', message.content)

def monolithic_chat(chat: ChatThread) -> str:
    """
    Returns a single-string representation of the entire chat thread.
    """
    return concat_documents(*(monolithic_message(message) for message in chat))

__all__ = [
    'monolithic_message',
    'monolithic_chat',
]
