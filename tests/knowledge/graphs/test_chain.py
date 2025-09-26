from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.graphs.chain import KnowledgeCrawlerChain
from llobot.knowledge.graphs.crawler import KnowledgeCrawler
from llobot.utils.values import ValueTypeMixin

class SimpleCrawler(KnowledgeCrawler, ValueTypeMixin):
    _source: Path
    _target: Path
    def __init__(self, source: str, target: str):
        self._source = Path(source)
        self._target = Path(target)
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
    assert list(graph[Path('a')].sorted()) == [Path('b')]
    assert list(graph[Path('b')].sorted()) == [Path('c')]

def test_chain_flattening():
    c1 = SimpleCrawler('a', 'b')
    c2 = SimpleCrawler('b', 'c')
    c3 = SimpleCrawler('c', 'd')
    chain1 = KnowledgeCrawlerChain(c1, c2)
    chain2 = KnowledgeCrawlerChain(chain1, c3)
    assert chain2._crawlers == (c1, c2, c3)
