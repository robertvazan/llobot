from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets
import llobot.knowledge.trees

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

@lru_cache
def overviews(overviews_subset: KnowledgeSubset | None = None) -> GraphScraper:
    """
    Creates a scraper that links regular files to overview files in their directories and ancestor directories.

    Args:
        overviews_subset: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A GraphScraper that creates links to overview files.
    """
    if overviews_subset is None:
        overviews_subset = llobot.knowledge.subsets.overviews()

    def scrape_overviews(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        tree = llobot.knowledge.trees.lexicographical(knowledge)

        # For each tree node (directory)
        for subtree in tree.all_trees:

            # Find overview files
            for overview_file in subtree.file_paths:
                if overview_file in overviews_subset:

                    # Link regular files to the overview file
                    for regular_file in subtree.all_paths:
                        if regular_file not in overviews_subset:
                            builder.add(regular_file, overview_file)

        return builder.build()

    return create(scrape_overviews)

@cache
def standard() -> GraphScraper:
    from llobot.scrapers import python, java, rust
    return (
        overviews()
        | python.standard()
        | java.standard()
        | rust.standard())

__all__ = [
    'GraphScraper',
    'none',
    'create',
    'overviews',
    'standard',
]
