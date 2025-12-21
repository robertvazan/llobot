from pathlib import PurePosixPath
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.indexes import KnowledgeIndex

def test_graph_init():
    graph = KnowledgeGraph({
        PurePosixPath('a'): KnowledgeIndex(['b', 'c']),
        PurePosixPath('b'): KnowledgeIndex(['c']),
    })
    assert len(graph) == 2
    assert PurePosixPath('a') in graph
    assert PurePosixPath('c') not in graph

def test_graph_eq_hash():
    g1 = KnowledgeGraphBuilder()
    g1.add(PurePosixPath('a'), PurePosixPath('b'))
    g1.add(PurePosixPath('a'), PurePosixPath('c'))
    graph1 = g1.build()

    g2 = KnowledgeGraphBuilder()
    g2.add(PurePosixPath('a'), PurePosixPath('c'))
    g2.add(PurePosixPath('a'), PurePosixPath('b'))
    graph2 = g2.build()

    g3 = KnowledgeGraphBuilder()
    g3.add(PurePosixPath('a'), PurePosixPath('b'))
    graph3 = g3.build()

    assert graph1 == graph2
    assert hash(graph1) == hash(graph2)
    assert graph1 != graph3
    assert {graph1, graph2} == {graph1}

def test_graph_keys():
    graph = KnowledgeGraph({
        PurePosixPath('a'): KnowledgeIndex(['b']),
        PurePosixPath('b'): KnowledgeIndex(['c']),
    })
    assert graph.keys() == KnowledgeIndex(['a', 'b'])

def test_graph_links():
    builder = KnowledgeGraphBuilder()
    builder.add(PurePosixPath('a'), PurePosixPath('b'))
    builder.add(PurePosixPath('a'), PurePosixPath('c'))
    graph = builder.build()
    links = set(graph.links())
    assert links == {(PurePosixPath('a'), PurePosixPath('b')), (PurePosixPath('a'), PurePosixPath('c'))}

def test_graph_union():
    g1 = KnowledgeGraphBuilder()
    g1.add(PurePosixPath('a'), PurePosixPath('b'))
    graph1 = g1.build()

    g2 = KnowledgeGraphBuilder()
    g2.add(PurePosixPath('b'), PurePosixPath('c'))
    graph2 = g2.build()

    merged = graph1 | graph2
    assert merged.keys() == KnowledgeIndex(['a', 'b'])
    assert merged[PurePosixPath('a')] == KnowledgeIndex(['b'])
    assert merged[PurePosixPath('b')] == KnowledgeIndex(['c'])

def test_graph_reverse():
    builder = KnowledgeGraphBuilder()
    builder.add(PurePosixPath('a'), PurePosixPath('b'))
    builder.add(PurePosixPath('a'), PurePosixPath('c'))
    graph = builder.build()
    reversed_graph = graph.reverse()

    assert reversed_graph.keys() == KnowledgeIndex(['b', 'c'])
    assert reversed_graph[PurePosixPath('a')] == KnowledgeIndex()
    assert reversed_graph[PurePosixPath('b')] == KnowledgeIndex(['a'])
    assert reversed_graph[PurePosixPath('c')] == KnowledgeIndex(['a'])

def test_graph_symmetrical():
    builder = KnowledgeGraphBuilder()
    builder.add(PurePosixPath('a'), PurePosixPath('b'))
    graph = builder.build()
    symmetrical = graph.symmetrical()

    assert symmetrical.keys() == KnowledgeIndex(['a', 'b'])
    assert symmetrical[PurePosixPath('a')] == KnowledgeIndex(['b'])
    assert symmetrical[PurePosixPath('b')] == KnowledgeIndex(['a'])
