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
    Creates a scraper that links files to overview files in their directories.

    Links every non-overview file in every directory to every overview file in the same directory.
    Also links overview files in child directories to overview files in parent directories.

    Args:
        overviews_subset: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A GraphScraper that creates overview-based links.
    """
    if overviews_subset is None:
        overviews_subset = llobot.knowledge.subsets.overviews()

    def scrape_overviews(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        tree = llobot.knowledge.trees.lexicographical(knowledge)

        # For each tree node (directory)
        for subtree in tree.all_trees:

            # For each overview file in it
            for overview_file in subtree.file_paths:
                if overview_file in overviews_subset:

                    # Link regular files to overview files in the same directory
                    for regular_file in subtree.file_paths:
                        if regular_file not in overviews_subset:
                            builder.add(regular_file, overview_file)

                    # Link overview files in subdirectories to parent overview files
                    for child in tree.subtrees:
                        for child_overview in child.file_paths:
                            if child_overview in overviews_subset:
                                builder.add(child_overview, overview_file)

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
