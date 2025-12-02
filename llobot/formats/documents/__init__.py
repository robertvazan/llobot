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
from pathlib import Path
from llobot.chats.thread import ChatThread
from llobot.formats.affirmations import affirmation_turn

class DocumentFormat:
    """
    Base class for document formats that handle document serialization.
    """

    def render(self, path: Path, content: str) -> str:
        """
        Renders a document into a string representation.

        Args:
            path: The path of the document.
            content: The content of the document.

        Returns:
            Formatted string.
        """
        raise NotImplementedError

    def render_chat(self, path: Path, content: str) -> ChatThread:
        """
        Renders a document as a chat thread.

        Args:
            path: The path of the document.
            content: The content of the document.

        Returns:
            A chat thread containing the rendered document.
        """
        rendered = self.render(path, content)
        return affirmation_turn(rendered)

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
