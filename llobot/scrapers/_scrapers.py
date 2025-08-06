from __future__ import annotations
from functools import cache
from collections import defaultdict
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.links import Link

class GraphScraper:
    def scrape(self, knowledge: Knowledge) -> KnowledgeGraph:
        return KnowledgeGraph()

    def __call__(self, knowledge: Knowledge) -> KnowledgeGraph:
        return self.scrape(knowledge)

    def __or__(self, other: GraphScraper) -> GraphScraper:
        return create(lambda knowledge: self(knowledge) | other(knowledge))

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
