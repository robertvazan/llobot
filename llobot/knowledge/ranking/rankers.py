from __future__ import annotations
from functools import cache
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking

class KnowledgeRanker:
    """
    Base class for knowledge ranking strategies.

    A ranker defines a method to create an ordered list of documents from a
    `Knowledge` base.
    """
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        """
        Creates a ranking for the given knowledge.

        Args:
            knowledge: The knowledge base to rank.

        Returns:
            A `KnowledgeRanking` object with an ordered list of document paths.
        """
        raise NotImplementedError

@cache
def standard_ranker() -> KnowledgeRanker:
    """
    Returns the standard knowledge ranker.

    The standard ranker sorts documents lexicographically, but prioritizes
    overview files to appear before their siblings in each directory.
    """
    # Local import to avoid circular dependency
    from llobot.knowledge.ranking.overviews import OverviewsBeforeSiblingsRanker
    return OverviewsBeforeSiblingsRanker()

__all__ = [
    'KnowledgeRanker',
    'standard_ranker',
]
