from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.knowledge.trees import coerce_tree

class GraphScraper:
    def scrape(self, knowledge: Knowledge) -> KnowledgeGraph:
        return KnowledgeGraph()

    def __call__(self, knowledge: Knowledge) -> KnowledgeGraph:
        return _scrape_cached(self, knowledge)

    def __or__(self, other: 'GraphScraper') -> 'GraphScraper':
        return create_scraper(lambda knowledge: self.scrape(knowledge) | other.scrape(knowledge))

@lru_cache(maxsize=2)
def _scrape_cached(scraper: GraphScraper, knowledge: Knowledge) -> KnowledgeGraph:
    return scraper.scrape(knowledge)

@cache
def no_scraper() -> GraphScraper:
    return GraphScraper()

def create_scraper(scrape: Callable[[Knowledge], KnowledgeGraph]) -> GraphScraper:
    class LambdaGraphScraper(GraphScraper):
        def scrape(self, knowledge: Knowledge) -> KnowledgeGraph:
            return scrape(knowledge)
    return LambdaGraphScraper()

@lru_cache
def overview_scraper(subset: KnowledgeSubset | None = None) -> GraphScraper:
    """
    Creates a scraper that links files to the nearest overview files.

    Args:
        subset: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A GraphScraper that creates links to nearest overview files.
    """
    if subset is None:
        subset = overviews_subset()

    def scrape_overviews(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        tree = coerce_tree(knowledge)
        seen = set()

        # Process subtrees in reverse order (deepest first) in order to link only to the nearest overviews
        for subtree in reversed(tree.all_trees):
            # Link to all overview files in the directory
            targets = [o for o in subtree.file_paths if o in subset]

            # Mark the files as seen only if they are linked to something
            if targets:
                regular_sources = [r for r in subtree.all_paths if r not in subset]
                overview_sources = [o for c in subtree.subtrees for o in c.all_paths if o in subset]
                sources = regular_sources + overview_sources

                for source in sources:
                    if source not in seen:
                        for target in targets:
                            builder.add(source, target)

                seen.update(sources)

        return builder.build()

    return create_scraper(scrape_overviews)

@cache
def standard_scraper() -> GraphScraper:
    from llobot.scrapers.java import standard_java_scraper
    from llobot.scrapers.python import standard_python_scraper
    from llobot.scrapers.rust import standard_rust_scraper
    return (
        overview_scraper()
        | standard_python_scraper()
        | standard_java_scraper()
        | standard_rust_scraper())

__all__ = [
    'GraphScraper',
    'no_scraper',
    'create_scraper',
    'overview_scraper',
    'standard_scraper',
]
