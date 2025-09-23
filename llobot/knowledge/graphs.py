from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from llobot.knowledge.indexes import KnowledgeIndex

class KnowledgeGraph:
    """
    An immutable directed graph where nodes are `pathlib.Path` objects.

    The graph is represented as a dictionary mapping source nodes to a
    `KnowledgeIndex` of their target nodes.
    """
    _graph: dict[Path, KnowledgeIndex]
    _hash: int | None

    def __init__(self, graph: dict[Path, KnowledgeIndex] = {}):
        """
        Initializes a new `KnowledgeGraph`.

        Args:
            graph: A dictionary representing the graph's adjacency list.
        """
        self._graph = graph
        self._hash = None

    def __repr__(self) -> str:
        return str(self._graph)

    def keys(self) -> KnowledgeIndex:
        """Returns a `KnowledgeIndex` of all source nodes in the graph."""
        return KnowledgeIndex(self._graph.keys())

    def __len__(self) -> int:
        return len(self._graph)

    def __bool__(self) -> bool:
        return bool(self._graph)

    def __eq__(self, other) -> bool:
        if not isinstance(other, KnowledgeGraph):
            return NotImplemented
        return self._graph == other._graph

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._graph.items()))
        return self._hash

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
        builder = KnowledgeGraphBuilder()
        for source, target in self.links():
            builder.add(target, source)
        return builder.build()

    def symmetrical(self) -> KnowledgeGraph:
        """
        Returns a symmetrical graph containing both original and reversed links.
        """
        return self | self.reverse()

class KnowledgeGraphBuilder:
    """
    A mutable builder for constructing `KnowledgeGraph` instances.
    """
    _graph: defaultdict[Path, set[Path]]

    def __init__(self):
        """Initializes an empty `KnowledgeGraphBuilder`."""
        self._graph = defaultdict(set)

    def add(self, source: Path, target: Path):
        """
        Adds a directed link to the graph.

        Self-loops are ignored.

        Args:
            source: The source node.
            target: The target node.
        """
        if source != target:
            self._graph[source].add(target)

    def build(self) -> KnowledgeGraph:
        """
        Constructs an immutable `KnowledgeGraph` from the current state.
        """
        return KnowledgeGraph({path: KnowledgeIndex(targets) for path, targets in self._graph.items()})

__all__ = [
    'KnowledgeGraph',
    'KnowledgeGraphBuilder',
]
