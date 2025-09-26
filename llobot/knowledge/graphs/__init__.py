"""
Data structures for representing knowledge as a directed graph.

This package provides `KnowledgeGraph` for representing relationships between
documents and a `KnowledgeGraphBuilder` for constructing graphs. It also includes
a `KnowledgeCrawler` framework for automatically building graphs from `Knowledge`
by analyzing source code.

Submodules
----------
builder
    `KnowledgeGraphBuilder` for mutable graph construction.
crawler
    `KnowledgeCrawler` for building graphs from `Knowledge`.
chain
    `KnowledgeCrawlerChain` for combining crawlers.
dummy
    `DummyCrawler` for a no-op crawler.
overview
    Crawler that links documents to overview files.
java
    Crawlers for Java source code.
python
    Crawlers for Python source code.
rust
    Crawlers for Rust source code.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterator
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge.indexes import KnowledgeIndex

class KnowledgeGraph(ValueTypeMixin):
    """
    An immutable directed graph where nodes are `pathlib.Path` objects.

    The graph is represented as a dictionary mapping source nodes to a
    `KnowledgeIndex` of their target nodes.
    """
    _graph: dict[Path, KnowledgeIndex]

    def __init__(self, graph: dict[Path, KnowledgeIndex] = {}):
        """
        Initializes a new `KnowledgeGraph`.

        Args:
            graph: A dictionary representing the graph's adjacency list.
        """
        self._graph = graph

    def __repr__(self) -> str:
        return str(self._graph)

    def keys(self) -> KnowledgeIndex:
        """Returns a `KnowledgeIndex` of all source nodes in the graph."""
        return KnowledgeIndex(self._graph.keys())

    def __len__(self) -> int:
        return len(self._graph)

    def __bool__(self) -> bool:
        return bool(self._graph)

    def __contains__(self, source: Path) -> bool:
        return source in self._graph

    def __getitem__(self, source: Path) -> KnowledgeIndex:
        """
        Gets the `KnowledgeIndex` of targets for a given source node.

        Returns an empty index if the source node is not in the graph.
        """
        return self._graph.get(source, KnowledgeIndex())

    def __iter__(self) -> Iterator[(Path, KnowledgeIndex)]:
        return iter(self._graph.items())

    def links(self) -> Iterator[(Path, Path)]:
        """
        Iterates over all links (edges) in the graph.

        Yields:
            A tuple of (source, target) for each link.
        """
        for source, targets in self:
            for target in targets:
                yield source, target

    def __or__(self, other: KnowledgeGraph) -> KnowledgeGraph:
        """
        Merges this graph with another, returning the union of their links.
        """
        from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
        builder = KnowledgeGraphBuilder()
        for source, target in self.links():
            builder.add(source, target)
        for source, target in other.links():
            builder.add(source, target)
        return builder.build()

    def reverse(self) -> KnowledgeGraph:
        """
        Returns a new graph with all links reversed.
        """
        from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
        builder = KnowledgeGraphBuilder()
        for source, target in self.links():
            builder.add(target, source)
        return builder.build()

    def symmetrical(self) -> KnowledgeGraph:
        """
        Returns a symmetrical graph containing both original and reversed links.
        """
        return self | self.reverse()

__all__ = [
    'KnowledgeGraph',
]
