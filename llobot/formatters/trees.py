from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from typing import Callable
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge.trees import KnowledgeTree, coerce_tree
from llobot.text import concat_documents, markdown_code_details

class TreeFormatter:
    """
    Interface for formatting knowledge trees as Markdown text.

    Tree formatters take a KnowledgeTree and render it as a human-readable Markdown string.
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

    def __call__(self, tree: KnowledgeTree) -> str:
        """Convenience method for calling render()."""
        return self.render(tree)

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

def create_tree_formatter(function: Callable[[KnowledgeTree], str]) -> TreeFormatter:
    """
    Creates a tree formatter from a function.

    Args:
        function: Function that takes a KnowledgeTree and returns a Markdown string.

    Returns:
        A TreeFormatter that uses the provided function.
    """
    class LambdaTreeFormatter(TreeFormatter):
        def render(self, tree: KnowledgeTree) -> str:
            return function(tree)
    return LambdaTreeFormatter()

@lru_cache
def flat_tree_formatter(title: str) -> TreeFormatter:
    """
    Creates a tree formatter that lists all file paths in a flat list.

    The formatter renders all paths from the tree in a single code block
    within a collapsible details/summary section.

    Args:
        title: Title to use for the details/summary section.

    Returns:
        A TreeFormatter that renders paths as a flat list.
    """
    def render_flat(tree: KnowledgeTree) -> str:
        paths = tree.all_paths
        if not paths:
            return ''
        file_list = '\n'.join(str(path) for path in paths)
        return markdown_code_details(title, '', file_list)
    return create_tree_formatter(render_flat)

@lru_cache
def grouped_tree_formatter(title: str) -> TreeFormatter:
    """
    Creates a tree formatter that groups files by directory.

    The formatter renders files grouped by their containing directory, with
    directory headers and files listed underneath. Groups are separated by
    empty lines. Root directory files (base path '.') are listed without a header.

    Args:
        title: Title to use for the details/summary section.

    Returns:
        A TreeFormatter that renders paths grouped by directory.
    """
    def render_grouped(tree: KnowledgeTree) -> str:
        sections = []
        for subtree in tree.all_trees:
            lines = []

            # Add header unless this is root with base path '.'
            if subtree.base != Path('.'):
                lines.append(f'In {subtree.base}:')

            # Add files
            for filename in subtree.files:
                lines.append(f'- {filename}')

            # Add subdirectories
            for directory in subtree.directories:
                lines.append(f'- {directory}/')

            sections.append('\n'.join(lines))

        if not sections:
            return ''

        content = concat_documents(*sections)
        return markdown_code_details(title, '', content)

    return create_tree_formatter(render_grouped)

@lru_cache
def standard_tree_formatter(title: str = 'Files') -> TreeFormatter:
    """
    Creates the standard tree formatter to be used by default.

    The standard formatter groups files by directory with a default title of 'Files'.

    Args:
        title: Title to use for the details/summary section.

    Returns:
        The standard TreeFormatter (currently grouped formatting).
    """
    return grouped_tree_formatter(title)

__all__ = [
    'TreeFormatter',
    'create_tree_formatter',
    'flat_tree_formatter',
    'grouped_tree_formatter',
    'standard_tree_formatter',
]
