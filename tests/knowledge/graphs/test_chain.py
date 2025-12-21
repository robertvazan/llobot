from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.graphs.chain import KnowledgeCrawlerChain
from llobot.knowledge.graphs.crawler import KnowledgeCrawler
from llobot.utils.values import ValueTypeMixin

class SimpleCrawler(KnowledgeCrawler, ValueTypeMixin):
    _source: PurePosixPath
    _target: PurePosixPath
    def __init__(self, source: str, target: str):
        self._source = PurePosixPath(source)
        self._target = PurePosixPath(target)
    def crawl(self, knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        builder.add(self._source, self._target)
        return builder.build()

def test_chain():
    c1 = SimpleCrawler('a', 'b')
    c2 = SimpleCrawler('b', 'c')
    chain = KnowledgeCrawlerChain(c1, c2)
    graph = chain.crawl(Knowledge())
    assert len(graph) == 2
    assert list(graph[PurePosixPath('a')].sorted()) == [PurePosixPath('b')]
    assert list(graph[PurePosixPath('b')].sorted()) == [PurePosixPath('c')]

def test_chain_flattening():
    c1 = SimpleCrawler('a', 'b')
    c2 = SimpleCrawler('b', 'c')
    c3 = SimpleCrawler('c', 'd')
    chain1 = KnowledgeCrawlerChain(c1, c2)
    chain2 = KnowledgeCrawlerChain(chain1, c3)
    assert chain2._crawlers == (c1, c2, c3)
