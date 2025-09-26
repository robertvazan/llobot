"""
Index format that lists all file paths in a flat list.
"""
from __future__ import annotations
from llobot.formats.indexes import IndexFormat
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking.rankers import KnowledgeRanker, standard_ranker
from llobot.utils.values import ValueTypeMixin

class FlatIndexFormat(IndexFormat, ValueTypeMixin):
    """
    An index format that lists all file paths in a flat list.
    """
    _ranker: KnowledgeRanker

    def __init__(self, *, ranker: KnowledgeRanker | None = None):
        """
        Creates a new flat index format.

        Args:
            ranker: The ranker to use for sorting paths. Defaults to the
                    standard ranker.
        """
        self._ranker = ranker if ranker is not None else standard_ranker()

    def render(self, knowledge: Knowledge) -> str:
        """
        Renders a knowledge index as a flat list of paths.

        The paths are sorted using the configured ranker.

        Args:
            knowledge: The knowledge to render.

        Returns:
            A string with a flat list of all paths in the index.
        """
        if not knowledge:
            return ''
        ranking = self._ranker.rank(knowledge)
        if not ranking:
            return ''
        return '\n'.join(str(path) for path in ranking)

__all__ = [
    'FlatIndexFormat',
]
