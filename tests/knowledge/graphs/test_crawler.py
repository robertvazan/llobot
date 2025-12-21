from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.graphs.crawler import KnowledgeCrawler
from llobot.knowledge.graphs.dummy import DummyCrawler
from llobot.utils.values import ValueTypeMixin

class SimpleCrawler(KnowledgeCrawler, ValueTypeMixin):
    _source: str
    _target: str
    def __init__(self, source: str, target: str):
        self._source = source
        self._target = target
    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        builder.add(PurePosixPath(self._source), PurePosixPath(self._target))
        return builder.build()

def test_or():
    c1 = SimpleCrawler('a', 'b')
    c2 = SimpleCrawler('b', 'c')
    chain = c1 | c2
    graph = chain.crawl(Knowledge())
    assert len(graph) == 2
    assert list(graph[PurePosixPath('a')].sorted()) == [PurePosixPath('b')]
    assert list(graph[PurePosixPath('b')].sorted()) == [PurePosixPath('c')]

def test_dummy_crawler():
    crawler = DummyCrawler()
    graph = crawler.crawl(Knowledge())
    assert not graph
