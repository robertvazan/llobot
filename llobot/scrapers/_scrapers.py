from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph

class GraphScraper:
    def scrape(self, knowledge: Knowledge) -> KnowledgeGraph:
        return KnowledgeGraph()

    def __call__(self, knowledge: Knowledge) -> KnowledgeGraph:
        return _scrape_cached(self, knowledge)

    def __or__(self, other: 'GraphScraper') -> 'GraphScraper':
        return create(lambda knowledge: self.scrape(knowledge) | other.scrape(knowledge))

@lru_cache(maxsize=2)
def _scrape_cached(scraper: GraphScraper, knowledge: Knowledge) -> KnowledgeGraph:
    return scraper.scrape(knowledge)

@cache
def none() -> GraphScraper:
    return GraphScraper()

def create(scrape: Callable[[Knowledge], KnowledgeGraph]) -> GraphScraper:
    class LambdaGraphScraper(GraphScraper):
        def scrape(self, knowledge: Knowledge) -> KnowledgeGraph:
            return scrape(knowledge)
    return LambdaGraphScraper()

@cache
def standard() -> GraphScraper:
    from llobot.scrapers import python, java, rust
    return (
        python.standard()
        | java.standard()
        | rust.standard())

__all__ = [
    'GraphScraper',
    'none',
    'create',
    'standard',
]
