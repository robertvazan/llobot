"""
Hierarchical directory tree formatting.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.trees import KnowledgeTree, coerce_tree
from llobot.formats.affirmations import affirmation_turn

class TreeFormat:
    """
    Interface for formatting knowledge trees as Markdown text.

    Tree formats take a KnowledgeTree and render it as a human-readable Markdown string.
    """

    def render(self, tree: KnowledgeTree) -> str:
        """
        Renders a knowledge tree as Markdown text.

        Args:
            tree: The knowledge tree to render.

        Returns:
            Markdown representation of the tree.
        """
        raise NotImplementedError

    def render_chat(self, tree: KnowledgeTree) -> ChatBranch:
        """
        Renders a knowledge tree as a chat branch.

        Args:
            tree: The knowledge tree to render.

        Returns:
            A chat branch containing the rendered tree, or an empty branch.
        """
        rendered = self.render(tree)
        return affirmation_turn(rendered)

    def render_sorted(self, material: KnowledgeIndex | Knowledge) -> str:
        """
        Renders knowledge material as a tree after converting and sorting it.

        This method converts the input material to a KnowledgeTree using lexicographical
        ordering and then renders it.

        Args:
            material: Knowledge index or index precursor to render.

        Returns:
            Markdown representation of the sorted tree.
        """
        tree = coerce_tree(material)
        return self.render(tree)

    def render_sorted_chat(self, material: KnowledgeIndex | Knowledge) -> ChatBranch:
        """
        Renders knowledge material as a tree after converting and sorting it.

        Args:
            material: Knowledge index or index precursor to render.

        Returns:
            A chat branch containing the rendered tree.
        """
        tree = coerce_tree(material)
        return self.render_chat(tree)

def standard_tree_format() -> TreeFormat:
    """
    Creates the standard tree format to be used by default.

    Returns:
        The standard TreeFormat.
    """
    from llobot.formats.trees.grouped import GroupedTreeFormat
    return GroupedTreeFormat()

__all__ = [
    'TreeFormat',
    'standard_tree_format',
]
