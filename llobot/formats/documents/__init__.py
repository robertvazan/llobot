"""
Formats for rendering documents.

This package provides formatters that can serialize documents into a
human-readable text format suitable for including in LLM prompts.

Submodules
----------
details
    An implementation of `DocumentFormat` using HTML `<details>` tags.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread

class DocumentFormat:
    """
    Base class for document formats that handle document serialization.
    """

    def render(self, path: PurePosixPath, content: str) -> str:
        """
        Renders a document into a string representation.

        Implementations must ensure that this method never returns None
        or an empty string, as it is used to populate context where
        content presence is expected.

        Args:
            path: The path of the document.
            content: The content of the document.

        Returns:
            Formatted string.
        """
        raise NotImplementedError

    def render_chat(self, path: PurePosixPath, content: str) -> ChatThread:
        """
        Renders a document as a chat thread.

        Args:
            path: The path of the document.
            content: The content of the document.

        Returns:
            A chat thread containing the rendered document.
        """
        rendered = self.render(path, content)
        # While render() contract forbids empty strings, we keep this check for robustness.
        if not rendered.strip():
            return ChatThread()
        return ChatThread([ChatMessage(ChatIntent.SYSTEM, rendered)])

def standard_document_format() -> DocumentFormat:
    """
    Get the standard document format instance.

    Returns:
        The standard `DocumentFormat`.
    """
    from llobot.formats.documents.details import DetailsDocumentFormat
    return DetailsDocumentFormat()

__all__ = [
    'DocumentFormat',
    'standard_document_format',
]
