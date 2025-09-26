"""
Index format that groups files by directory.
"""
from __future__ import annotations
from pathlib import Path
from llobot.formats.indexes import IndexFormat
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking.rankers import KnowledgeRanker, standard_ranker
from llobot.knowledge.trees.ranked import ranked_tree
from llobot.utils.text import concat_documents
from llobot.utils.values import ValueTypeMixin

class GroupedIndexFormat(IndexFormat, ValueTypeMixin):
    """
    An index format that groups files by directory.

    The format renders files grouped by their containing directory, with
    directory headers and files listed underneath. Groups are separated by
    empty lines. Root directory files (base path '.') are listed without a header.
    """
    _ranker: KnowledgeRanker

    def __init__(self, *, ranker: KnowledgeRanker | None = None):
        """
        Creates a new grouped index format.

        Args:
            ranker: The ranker to use for sorting paths. Defaults to the
                    standard ranker.
        """
        self._ranker = ranker if ranker is not None else standard_ranker()

    def render(self, knowledge: Knowledge) -> str:
        """
        Renders a knowledge index by grouping files by directory.

        Args:
            knowledge: The knowledge to render.

        Returns:
            A Markdown string with files grouped by directory.
        """
        if not knowledge:
            return ''

        ranking = self._ranker.rank(knowledge)
        tree = ranked_tree(ranking)

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

        return concat_documents(*sections)

__all__ = [
    'GroupedIndexFormat',
]
