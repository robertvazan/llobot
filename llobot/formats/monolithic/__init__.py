"""
Formatting chats as a single monolithic string.

This package provides the `MonolithicFormat` interface for rendering an entire
`ChatThread` as a single string. This is useful for debugging, logging, or for
simple models that consume a flat text prompt.

Submodules
----------
separator
    A `MonolithicFormat` that joins messages with a separator.
details
    A `MonolithicFormat` that wraps each message in an HTML `<details>` tag.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread

class MonolithicFormat:
    """
    Interface for formatting chat threads as a single string.
    """
    def render(self, chat: ChatThread) -> str:
        """
        Renders a chat thread as a single string.

        Args:
            chat: The chat thread to render.

        Returns:
            The string representation of the chat.
        """
        raise NotImplementedError

def standard_monolithic_format() -> MonolithicFormat:
    """
    Creates the standard monolithic format to be used by default.

    Returns:
        The standard `MonolithicFormat`.
    """
    from llobot.formats.monolithic.separator import SeparatorMonolithicFormat
    return SeparatorMonolithicFormat()

__all__ = [
    'MonolithicFormat',
    'standard_monolithic_format',
]
