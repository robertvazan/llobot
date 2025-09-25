"""
Index format that lists all file paths in a flat list.
"""
from __future__ import annotations
from llobot.formats.indexes import IndexFormat
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndexPrecursor, coerce_index
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

    def render(self, index: KnowledgeIndexPrecursor) -> str:
        """
        Renders a knowledge index as a flat list of paths.

        The paths are sorted using the configured ranker.

        Args:
            index: The knowledge index to render.

        Returns:
            A string with a flat list of all paths in the index.
        """
        coerced_index = coerce_index(index)
        if not coerced_index:
            return ''
        knowledge = Knowledge({path: '' for path in coerced_index})
        ranking = self._ranker.rank(knowledge)
        if not ranking:
            return ''
        return '\n'.join(str(path) for path in ranking)

__all__ = [
    'FlatIndexFormat',
]
