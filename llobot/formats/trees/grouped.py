"""
Tree format that groups files by directory.
"""
from __future__ import annotations
from pathlib import Path
from llobot.knowledge.trees import KnowledgeTree
from llobot.formats.trees import TreeFormat
from llobot.utils.text import concat_documents, markdown_code_details
from llobot.utils.values import ValueTypeMixin

class GroupedTreeFormat(TreeFormat, ValueTypeMixin):
    """
    A tree format that groups files by directory.

    The format renders files grouped by their containing directory, with
    directory headers and files listed underneath. Groups are separated by
    empty lines. Root directory files (base path '.') are listed without a header.
    """
    _title: str

    def __init__(self, title: str = 'Project files'):
        """
        Creates a new grouped tree format.

        Args:
            title: Title to use for the details/summary section.
        """
        self._title = title

    def render(self, tree: KnowledgeTree) -> str:
        """
        Renders a knowledge tree by grouping files by directory.

        Args:
            tree: The knowledge tree to render.

        Returns:
            A Markdown string with files grouped by directory.
        """
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

            if lines:
                sections.append('\n'.join(lines))

        if not sections:
            return ''

        content = concat_documents(*sections)
        return markdown_code_details(self._title, '', content)

__all__ = [
    'GroupedTreeFormat',
]
