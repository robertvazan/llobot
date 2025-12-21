from pathlib import PurePosixPath
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.indexes import KnowledgeIndex

def test_builder():
    builder = KnowledgeGraphBuilder()
    builder.add(PurePosixPath('a'), PurePosixPath('b'))
    builder.add(PurePosixPath('a'), PurePosixPath('c'))
    builder.add(PurePosixPath('b'), PurePosixPath('c'))
    builder.add(PurePosixPath('a'), PurePosixPath('a')) # self-loop should be ignored
    graph = builder.build()
    assert len(graph) == 2
    assert graph[PurePosixPath('a')] == KnowledgeIndex(['b', 'c'])
    assert graph[PurePosixPath('b')] == KnowledgeIndex(['c'])
    assert graph[PurePosixPath('c')] == KnowledgeIndex()
