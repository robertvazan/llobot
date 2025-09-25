"""
Tests for `llobot.knowledge.indexes`.
"""
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex, coerce_index
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.subsets.pattern import PatternSubset

INDEX = KnowledgeIndex(['a/b.txt', 'a/c.txt', 'd.txt'])

def test_knowledge_index_init():
    assert len(KnowledgeIndex()) == 0
    assert len(INDEX) == 3

def test_knowledge_index_eq_hash():
    i2 = KnowledgeIndex(['d.txt', 'a/c.txt', 'a/b.txt'])
    assert INDEX == i2
    assert hash(INDEX) == hash(i2)
    assert INDEX != KnowledgeIndex(['x.txt'])
    assert {INDEX, i2} == {INDEX}

def test_knowledge_index_contains():
    assert Path('a/b.txt') in INDEX
    assert 'a/b.txt' in INDEX
    assert 'x.txt' not in INDEX

def test_knowledge_index_sorted():
    ranking = INDEX.sorted()
    # default is preorder lexicographical
    assert ranking == KnowledgeRanking(['d.txt', 'a/b.txt', 'a/c.txt'])

def test_knowledge_index_reversed():
    ranking = INDEX.reversed()
    assert ranking == KnowledgeRanking(['a/c.txt', 'a/b.txt', 'd.txt'])

def test_knowledge_index_filter():
    filtered = INDEX & PatternSubset('a/*')
    assert filtered == KnowledgeIndex(['a/b.txt', 'a/c.txt'])

def test_knowledge_index_union():
    merged = INDEX | Path('x.txt')
    assert merged == KnowledgeIndex(['a/b.txt', 'a/c.txt', 'd.txt', 'x.txt'])
    merged2 = INDEX | KnowledgeIndex(['x.txt', 'y.txt'])
    assert merged2 == KnowledgeIndex(['a/b.txt', 'a/c.txt', 'd.txt', 'x.txt', 'y.txt'])

def test_knowledge_index_subtract():
    subtracted = INDEX - 'd.txt'
    assert subtracted == KnowledgeIndex(['a/b.txt', 'a/c.txt'])

def test_knowledge_index_paths():
    prefixed = 'a' / KnowledgeIndex(['b.txt'])
    assert prefixed == KnowledgeIndex(['a/b.txt'])
    subtree = INDEX / 'a'
    assert subtree == KnowledgeIndex(['b.txt', 'c.txt'])

def test_coerce_index():
    assert coerce_index(INDEX) is INDEX
    knowledge = Knowledge({
        Path('a/b.txt'): 'content',
        Path('a/c.txt'): 'content',
        Path('d.txt'): 'content',
    })
    assert coerce_index(knowledge) == INDEX
    assert coerce_index(KnowledgeRanking(['a.txt', 'b.txt'])) == KnowledgeIndex(['a.txt', 'b.txt'])

def test_coerce_index_invalid_type():
    from llobot.knowledge.scores import KnowledgeScores
    try:
        coerce_index(KnowledgeScores({Path('a.txt'): 1.0}))
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
