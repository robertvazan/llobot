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
    Creates a scraper that links files to the nearest overview files.

    Args:
        overviews_subset: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A GraphScraper that creates links to nearest overview files.
    """
    if overviews_subset is None:
        overviews_subset = llobot.knowledge.subsets.overviews()

    def scrape_overviews(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        tree = llobot.knowledge.trees.lexicographical(knowledge)
        seen = set()

        # Process subtrees in reverse order (deepest first) in order to link only to the nearest overviews
        for subtree in reversed(tree.all_trees):
            # Link to all overview files in the directory
            targets = [o for o in subtree.file_paths if o in overviews_subset]

            # Mark the files as seen only if they are linked to something
            if targets:
                regular_sources = [r for r in subtree.all_paths if r not in overviews_subset]
                overview_sources = [o for c in subtree.subtrees for o in c.all_paths if o in overviews_subset]
                sources = regular_sources + overview_sources

                for source in sources:
                    if source not in seen:
                        for target in targets:
                            builder.add(source, target)

                seen.update(sources)

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
