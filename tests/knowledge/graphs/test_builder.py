from pathlib import Path
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.indexes import KnowledgeIndex

def test_builder():
    builder = KnowledgeGraphBuilder()
    builder.add(Path('a'), Path('b'))
    builder.add(Path('a'), Path('c'))
    builder.add(Path('b'), Path('c'))
    builder.add(Path('a'), Path('a')) # self-loop should be ignored
    graph = builder.build()
    assert len(graph) == 2
    assert graph[Path('a')] == KnowledgeIndex(['b', 'c'])
    assert graph[Path('b')] == KnowledgeIndex(['c'])
    assert graph[Path('c')] == KnowledgeIndex()
