"""
A mutable builder for `KnowledgeGraph`.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import PurePosixPath
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.indexes import KnowledgeIndex

class KnowledgeGraphBuilder:
    """
    A mutable builder for constructing `KnowledgeGraph` instances.
    """
    _graph: defaultdict[PurePosixPath, set[PurePosixPath]]

    def __init__(self):
        """Initializes an empty `KnowledgeGraphBuilder`."""
        self._graph = defaultdict(set)

    def add(self, source: PurePosixPath, target: PurePosixPath):
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
    'KnowledgeGraphBuilder',
]
