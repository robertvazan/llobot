"""
A crawler that is a chain of other crawlers.
"""
from __future__ import annotations
from functools import lru_cache
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.crawler import KnowledgeCrawler

@lru_cache(maxsize=2)
def _crawl_cached(chain: 'KnowledgeCrawlerChain', knowledge: Knowledge) -> KnowledgeGraph:
    """
    Cached execution of a crawler chain.
    """
    graph = KnowledgeGraph()
    for crawler in chain._crawlers:
        graph |= crawler.crawl(knowledge)
    return graph

class KnowledgeCrawlerChain(KnowledgeCrawler, ValueTypeMixin):
    """
    A crawler that runs several crawlers in sequence and merges their graphs.

    The results of the `crawl` method are cached based on the chain's value
    and the knowledge base.
    """
    _crawlers: tuple[KnowledgeCrawler, ...]

    def __init__(self, *crawlers: KnowledgeCrawler):
        """
        Creates a new crawler chain.

        Args:
            *crawlers: The crawlers to include in the chain. The chain is
                       flattened if it contains other chains.
        """
        flattened = []
        for crawler in crawlers:
            if isinstance(crawler, KnowledgeCrawlerChain):
                flattened.extend(crawler._crawlers)
            else:
                flattened.append(crawler)
        self._crawlers = tuple(flattened)

    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        """
        Crawls the knowledge base using all crawlers in the chain.

        The execution is cached.

        Args:
            knowledge: The knowledge base to crawl.

        Returns:
            The merged `KnowledgeGraph` from all crawlers.
        """
        return _crawl_cached(self, knowledge)

__all__ = [
    'KnowledgeCrawlerChain',
]
