from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.solo import SoloSubset

KNOWLEDGE = Knowledge({
    Path('a/b.txt'): 'content b',
    Path('a/c.txt'): 'content c',
    Path('d.txt'): 'content d',
})

def test_knowledge_init():
    assert len(Knowledge()) == 0
    assert len(KNOWLEDGE) == 3

def test_knowledge_keys():
    assert KNOWLEDGE.keys() == KnowledgeIndex(['a/b.txt', 'a/c.txt', 'd.txt'])

def test_knowledge_cost():
    assert KNOWLEDGE.cost == len('content b') + len('content c') + len('content d')

def test_knowledge_eq_hash():
    k2 = Knowledge({
        Path('a/c.txt'): 'content c',
        Path('d.txt'): 'content d',
        Path('a/b.txt'): 'content b',
    })
    assert KNOWLEDGE == k2
    assert hash(KNOWLEDGE) == hash(k2)
    assert KNOWLEDGE != Knowledge({Path('a/b.txt'): 'changed'})
    assert {KNOWLEDGE, k2} == {KNOWLEDGE}

def test_knowledge_contains():
    assert Path('a/b.txt') in KNOWLEDGE
    assert 'a/b.txt' in KNOWLEDGE
    assert Path('x.txt') not in KNOWLEDGE

def test_knowledge_getitem():
    assert KNOWLEDGE[Path('a/b.txt')] == 'content b'
    assert KNOWLEDGE[Path('x.txt')] == ''

def test_knowledge_transform():
    transformed = KNOWLEDGE.transform(lambda path, content: content.upper())
    assert transformed[Path('a/b.txt')] == 'CONTENT B'

def test_knowledge_filter():
    filtered = KNOWLEDGE & SoloSubset(Path('a/b.txt'))
    assert filtered.keys() == KnowledgeIndex(['a/b.txt'])

def test_knowledge_union():
    other = Knowledge({Path('x.txt'): 'content x', Path('a/b.txt'): 'overwritten'})
    merged = KNOWLEDGE | other
    assert merged.keys() == KnowledgeIndex(['a/b.txt', 'a/c.txt', 'd.txt', 'x.txt'])
    assert merged[Path('a/b.txt')] == 'overwritten'

def test_knowledge_subtract():
    subtracted = KNOWLEDGE - SoloSubset(Path('d.txt'))
    assert subtracted.keys() == KnowledgeIndex(['a/b.txt', 'a/c.txt'])

def test_knowledge_paths():
    prefixed = 'a' / Knowledge({Path('b.txt'): 'content'})
    assert prefixed.keys() == KnowledgeIndex(['a/b.txt'])
    subtree = KNOWLEDGE / 'a'
    assert subtree.keys() == KnowledgeIndex(['b.txt', 'c.txt'])
