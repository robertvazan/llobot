from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge import Knowledge
from llobot.scrapers import Scraper

class KnowledgeGraph:
    _graph: dict[Path, KnowledgeIndex]
    _hash: int | None

    def __init__(self, graph: dict[Path, KnowledgeIndex]):
        self._graph = graph
        self._hash = None

    def __str__(self) -> str:
        return str(self._graph)

    def keys(self) -> KnowledgeIndex:
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
        return self._graph.get(source, KnowledgeIndex())

    def __iter__(self) -> Iterator[(Path, KnowledgeIndex)]:
        return iter(self._graph.items())

    def __or__(self, other: KnowledgeGraph) -> KnowledgeGraph:
        combined = defaultdict(KnowledgeIndex)
        for source, targets in self:
            combined[source] |= targets
        for source, targets in other:
            combined[source] |= targets
        return KnowledgeGraph(dict(combined))

    def reverse(self) -> KnowledgeGraph:
        backlinks = defaultdict(set)
        for source, targets in self:
            for target in targets:
                backlinks[target].add(source)
        return KnowledgeGraph({target: KnowledgeIndex(sources) for target, sources in backlinks.items()})

    def symmetrical(self) -> KnowledgeGraph:
        return self | self.reverse()

def crawl(knowledge: Knowledge, scraper: Scraper) -> KnowledgeGraph:
    graph = defaultdict(set)
    indexes = {}
    for source, content in knowledge:
        for link in scraper(source, content):
            for target in link.resolve_indexed(knowledge, indexes):
                if target != source:
                    graph[source].add(target)
    return KnowledgeGraph({path: KnowledgeIndex(targets) for path, targets in graph.items()})

__all__ = [
    'KnowledgeGraph',
    'crawl',
]
