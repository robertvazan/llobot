"""
A no-op crawler.
"""
from __future__ import annotations
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.graphs.crawler import KnowledgeCrawler

class DummyCrawler(KnowledgeCrawler, ValueTypeMixin):
    """
    A crawler that does nothing and returns an empty graph. It is a singleton-by-value.
    """
    pass

__all__ = [
    'DummyCrawler',
]
