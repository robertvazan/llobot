"""
Crawler that links files to the nearest overview files.
"""
from __future__ import annotations
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.graphs.crawler import KnowledgeCrawler
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.knowledge.trees import coerce_tree

class OverviewCrawler(KnowledgeCrawler, ValueTypeMixin):
    """
    A crawler that links files to the nearest overview files in parent directories.
    """
    _subset: KnowledgeSubset

    def __init__(self, *, subset: KnowledgeSubset | None = None):
        """
        Creates a new overview crawler.

        Args:
            subset: Subset defining overview files. Defaults to the standard one.
        """
        if subset is None:
            subset = overviews_subset()
        self._subset = subset

    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        """
        Crawls the knowledge base to link files to overview files.

        Args:
            knowledge: The knowledge base to crawl.

        Returns:
            A `KnowledgeGraph` with links to overview files.
        """
        builder = KnowledgeGraphBuilder()
        tree = coerce_tree(knowledge)
        seen = set()

        # Process subtrees in reverse order (deepest first) in order to link only to the nearest overviews
        for subtree in reversed(tree.all_trees):
            # Link to all overview files in the directory
            targets = [o for o in subtree.file_paths if o in self._subset]

            # Mark the files as seen only if they are linked to something
            if targets:
                regular_sources = [r for r in subtree.all_paths if r not in self._subset]
                overview_sources = [o for c in subtree.subtrees for o in c.all_paths if o in self._subset]
                sources = regular_sources + overview_sources

                for source in sources:
                    if source not in seen:
                        for target in targets:
                            builder.add(source, target)

                seen.update(sources)
        return builder.build()

__all__ = [
    'OverviewCrawler',
]
