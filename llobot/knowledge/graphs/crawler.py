"""
Base `KnowledgeCrawler` and standard crawler implementations.
"""
from __future__ import annotations
from functools import cache
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph

class KnowledgeCrawler:
    """
    Base class for knowledge crawling strategies.

    A crawler defines a method to create a `KnowledgeGraph` from a
    `Knowledge` base. Crawlers can be chained using the `|` operator.
    """
    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        """
        Creates a graph for the given knowledge.

        Args:
            knowledge: The knowledge base to crawl.

        Returns:
            A `KnowledgeGraph` object with links between documents.
        """
        return KnowledgeGraph()

    def __or__(self, other: KnowledgeCrawler) -> KnowledgeCrawler:
        """
        Chains this crawler with another one.

        Args:
            other: The crawler to append to the chain.

        Returns:
            A `KnowledgeCrawlerChain` of the two crawlers.
        """
        from llobot.knowledge.graphs.chain import KnowledgeCrawlerChain
        return KnowledgeCrawlerChain(self, other)

@cache
def standard_knowledge_crawler() -> KnowledgeCrawler:
    """
    Returns the standard knowledge crawler.

    The standard crawler combines crawlers for overview files and for Python,
    Java, and Rust source code.
    """
    from llobot.knowledge.graphs.java import standard_java_crawler
    from llobot.knowledge.graphs.overview import OverviewCrawler
    from llobot.knowledge.graphs.python import standard_python_crawler
    from llobot.knowledge.graphs.rust import standard_rust_crawler
    return (
        OverviewCrawler()
        | standard_python_crawler()
        | standard_java_crawler()
        | standard_rust_crawler())

__all__ = [
    'KnowledgeCrawler',
    'standard_knowledge_crawler',
]
