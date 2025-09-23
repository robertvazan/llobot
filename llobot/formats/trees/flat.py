"""
Tree format that lists all file paths in a flat list.
"""
from __future__ import annotations
from llobot.knowledge.trees import KnowledgeTree
from llobot.formats.trees import TreeFormat
from llobot.utils.text import markdown_code_details
from llobot.utils.values import ValueTypeMixin

class FlatTreeFormat(TreeFormat, ValueTypeMixin):
    """
    A tree format that lists all file paths in a flat list.

    The format renders all paths from the tree in a single code block
    within a collapsible details/summary section.
    """
    _title: str

    def __init__(self, title: str = 'Project files'):
        """
        Creates a new flat tree format.

        Args:
            title: Title to use for the details/summary section.
        """
        self._title = title

    def render(self, tree: KnowledgeTree) -> str:
        """
        Renders a knowledge tree as a flat list of paths.

        Args:
            tree: The knowledge tree to render.

        Returns:
            A Markdown string with a flat list of all paths in the tree.
        """
        paths = tree.all_paths
        if not paths:
            return ''
        file_list = '\n'.join(str(path) for path in paths)
        return markdown_code_details(self._title, '', file_list)

__all__ = [
    'FlatTreeFormat',
]
