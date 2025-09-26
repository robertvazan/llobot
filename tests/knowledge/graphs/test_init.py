from pathlib import Path
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.graphs.builder import KnowledgeGraphBuilder
from llobot.knowledge.indexes import KnowledgeIndex

def test_graph_init():
    graph = KnowledgeGraph({
        Path('a'): KnowledgeIndex(['b', 'c']),
        Path('b'): KnowledgeIndex(['c']),
    })
    assert len(graph) == 2
    assert Path('a') in graph
    assert Path('c') not in graph

def test_graph_eq_hash():
    g1 = KnowledgeGraphBuilder()
    g1.add(Path('a'), Path('b'))
    g1.add(Path('a'), Path('c'))
    graph1 = g1.build()

    g2 = KnowledgeGraphBuilder()
    g2.add(Path('a'), Path('c'))
    g2.add(Path('a'), Path('b'))
    graph2 = g2.build()

    g3 = KnowledgeGraphBuilder()
    g3.add(Path('a'), Path('b'))
    graph3 = g3.build()

    assert graph1 == graph2
    assert hash(graph1) == hash(graph2)
    assert graph1 != graph3
    assert {graph1, graph2} == {graph1}

def test_graph_keys():
    graph = KnowledgeGraph({
        Path('a'): KnowledgeIndex(['b']),
        Path('b'): KnowledgeIndex(['c']),
    })
    assert graph.keys() == KnowledgeIndex(['a', 'b'])

def test_graph_links():
    builder = KnowledgeGraphBuilder()
    builder.add(Path('a'), Path('b'))
    builder.add(Path('a'), Path('c'))
    graph = builder.build()
    links = set(graph.links())
    assert links == {(Path('a'), Path('b')), (Path('a'), Path('c'))}

def test_graph_union():
    g1 = KnowledgeGraphBuilder()
    g1.add(Path('a'), Path('b'))
    graph1 = g1.build()

    g2 = KnowledgeGraphBuilder()
    g2.add(Path('b'), Path('c'))
    graph2 = g2.build()

    merged = graph1 | graph2
    assert merged.keys() == KnowledgeIndex(['a', 'b'])
    assert merged[Path('a')] == KnowledgeIndex(['b'])
    assert merged[Path('b')] == KnowledgeIndex(['c'])

def test_graph_reverse():
    builder = KnowledgeGraphBuilder()
    builder.add(Path('a'), Path('b'))
    builder.add(Path('a'), Path('c'))
    graph = builder.build()
    reversed_graph = graph.reverse()

    assert reversed_graph.keys() == KnowledgeIndex(['b', 'c'])
    assert reversed_graph[Path('a')] == KnowledgeIndex()
    assert reversed_graph[Path('b')] == KnowledgeIndex(['a'])
    assert reversed_graph[Path('c')] == KnowledgeIndex(['a'])

def test_graph_symmetrical():
    builder = KnowledgeGraphBuilder()
    builder.add(Path('a'), Path('b'))
    graph = builder.build()
    symmetrical = graph.symmetrical()

    assert symmetrical.keys() == KnowledgeIndex(['a', 'b'])
    assert symmetrical[Path('a')] == KnowledgeIndex(['b'])
    assert symmetrical[Path('b')] == KnowledgeIndex(['a'])
