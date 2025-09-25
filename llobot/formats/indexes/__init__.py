"""
Formatting knowledge indexes.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.knowledge.indexes import KnowledgeIndexPrecursor
from llobot.formats.affirmations import affirmation_turn

class IndexFormat:
    """
    Interface for formatting knowledge indexes as Markdown text.

    Index formats take a KnowledgeIndexPrecursor and render it as a
    human-readable Markdown string. They are responsible for ranking.
    """
    def render(self, index: KnowledgeIndexPrecursor) -> str:
        """
        Renders a knowledge index as Markdown text.

        Args:
            index: The knowledge index (or precursor) to render.

        Returns:
            Markdown representation of the index.
        """
        raise NotImplementedError

    def render_chat(self, index: KnowledgeIndexPrecursor) -> ChatBranch:
        """
        Renders a knowledge index as a chat branch.

        Args:
            index: The knowledge index (or precursor) to render.

        Returns:
            A chat branch containing the rendered index, or an empty branch.
        """
        rendered = self.render(index)
        return affirmation_turn(rendered)

def standard_index_format() -> IndexFormat:
    """
    Creates the standard index format to be used by default.

    Returns:
        The standard IndexFormat.
    """
    from llobot.formats.indexes.details import DetailsIndexFormat
    from llobot.formats.indexes.grouped import GroupedIndexFormat
    return DetailsIndexFormat(GroupedIndexFormat())

__all__ = [
    'IndexFormat',
    'standard_index_format',
]
