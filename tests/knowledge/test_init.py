from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.solo import SoloSubset

KNOWLEDGE = Knowledge({
    PurePosixPath('a/b.txt'): 'content b',
    PurePosixPath('a/c.txt'): 'content c',
    PurePosixPath('d.txt'): 'content d',
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
        PurePosixPath('a/c.txt'): 'content c',
        PurePosixPath('d.txt'): 'content d',
        PurePosixPath('a/b.txt'): 'content b',
    })
    assert KNOWLEDGE == k2
    assert hash(KNOWLEDGE) == hash(k2)
    assert KNOWLEDGE != Knowledge({PurePosixPath('a/b.txt'): 'changed'})
    assert {KNOWLEDGE, k2} == {KNOWLEDGE}

def test_knowledge_contains():
    assert PurePosixPath('a/b.txt') in KNOWLEDGE
    assert 'a/b.txt' in KNOWLEDGE
    assert PurePosixPath('x.txt') not in KNOWLEDGE

def test_knowledge_getitem():
    assert KNOWLEDGE[PurePosixPath('a/b.txt')] == 'content b'
    assert KNOWLEDGE[PurePosixPath('x.txt')] == ''

def test_knowledge_transform():
    transformed = KNOWLEDGE.transform(lambda path, content: content.upper())
    assert transformed[PurePosixPath('a/b.txt')] == 'CONTENT B'

def test_knowledge_filter():
    filtered = KNOWLEDGE & SoloSubset(PurePosixPath('a/b.txt'))
    assert filtered.keys() == KnowledgeIndex(['a/b.txt'])

def test_knowledge_union():
    other = Knowledge({PurePosixPath('x.txt'): 'content x', PurePosixPath('a/b.txt'): 'overwritten'})
    merged = KNOWLEDGE | other
    assert merged.keys() == KnowledgeIndex(['a/b.txt', 'a/c.txt', 'd.txt', 'x.txt'])
    assert merged[PurePosixPath('a/b.txt')] == 'overwritten'

def test_knowledge_subtract():
    subtracted = KNOWLEDGE - SoloSubset(PurePosixPath('d.txt'))
    assert subtracted.keys() == KnowledgeIndex(['a/b.txt', 'a/c.txt'])

def test_knowledge_paths():
    prefixed = 'a' / Knowledge({PurePosixPath('b.txt'): 'content'})
    assert prefixed.keys() == KnowledgeIndex(['a/b.txt'])
    subtree = KNOWLEDGE / 'a'
    assert subtree.keys() == KnowledgeIndex(['b.txt', 'c.txt'])
