"""
Document delta format.
"""
from __future__ import annotations
from pathlib import Path
from llobot.chats.thread import ChatThread
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.builder import KnowledgeDeltaBuilder
from llobot.formats.affirmations import affirmation_turn

class DocumentDeltaFormat:
    """
    Base class for document delta formats that handle DocumentDelta serialization.

    Document delta formats can convert DocumentDelta objects to formatted strings
    and parse formatted text back into DocumentDelta objects.
    """

    def render(self, delta: DocumentDelta) -> str:
        """
        Renders a DocumentDelta into a string representation.

        Args:
            delta: The document delta to render.

        Returns:
            Formatted string.
        """
        raise NotImplementedError

    def render_chat(self, delta: DocumentDelta) -> ChatThread:
        """
        Renders a document delta as a chat thread.

        Args:
            delta: The document delta to render.

        Returns:
            A chat thread containing the rendered delta, or an empty thread.
        """
        rendered = self.render(delta)
        return affirmation_turn(rendered)

    def render_fresh(self, path: Path, content: str) -> str:
        """
        Renders a fresh document (new or modified).

        Args:
            path: The path of the document.
            content: The content of the document.

        Returns:
            The rendered string for the fresh document.
        """
        return self.render(DocumentDelta(path, content))

    def render_fresh_chat(self, path: Path, content: str) -> ChatThread:
        """
        Renders a fresh document (new or modified) as a chat thread.

        Args:
            path: The path of the document.
            content: The content of the document.

        Returns:
            A chat thread containing the rendered document.
        """
        return self.render_chat(DocumentDelta(path, content))

    def find(self, message: str) -> list[str]:
        """
        Finds all formatted delta strings in a message.

        Args:
            message: Text to search for formatted deltas.

        Returns:
            List of formatted delta strings found in the message.
        """
        return []

    def parse(self, formatted: str) -> DocumentDelta | None:
        """
        Parses a formatted string back into a DocumentDelta.

        Args:
            formatted: The formatted string to parse.

        Returns:
            DocumentDelta object or None if parsing fails.
        """
        return None

    def parse_message(self, message: str | ChatMessage) -> KnowledgeDelta:
        """
        Parses all deltas found in a chat message.

        Args:
            message: The message content to parse.

        Returns:
            A `KnowledgeDelta` containing all parsed document deltas.
        """
        from llobot.chats.message import ChatMessage
        if isinstance(message, ChatMessage):
            message = message.content

        builder = KnowledgeDeltaBuilder()
        for match in self.find(message):
            delta = self.parse(match)
            if delta:
                builder.add(delta)
        return builder.build()

    def parse_chat(self, chat: ChatThread) -> KnowledgeDelta:
        """
        Parses all deltas found in a chat thread.

        Args:
            chat: The chat thread to parse.

        Returns:
            A `KnowledgeDelta` containing all parsed document deltas.
        """
        builder = KnowledgeDeltaBuilder()
        for message in chat:
            builder.add(self.parse_message(message.content))
        return builder.build()

def standard_document_delta_format() -> DocumentDeltaFormat:
    """
    Get the standard document delta format instance.

    Returns:
        The standard `DocumentDeltaFormat`.
    """
    from llobot.formats.deltas.details import DetailsDocumentDeltaFormat
    return DetailsDocumentDeltaFormat()

__all__ = [
    'DocumentDeltaFormat',
    'standard_document_delta_format',
]
