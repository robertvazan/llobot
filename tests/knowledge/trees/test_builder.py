from pathlib import Path
from llobot.knowledge.trees.builder import KnowledgeTreeBuilder

def test_builder():
    builder = KnowledgeTreeBuilder()
    builder.add('a/b.txt')
    builder.add('a/c.txt')
    builder.add('d.txt')
    builder.add('a/e/f.txt')
    tree = builder.build()

    assert tree.base == Path('.')
    assert tree.files == ['d.txt']
    assert len(tree.subtrees) == 1
    
    subtree_a = tree.subtrees[0]
    assert subtree_a.base == Path('a')
    assert subtree_a.files == ['b.txt', 'c.txt']
    assert len(subtree_a.subtrees) == 1

    subtree_e = subtree_a.subtrees[0]
    assert subtree_e.base == Path('a/e')
    assert subtree_e.files == ['f.txt']
    assert not subtree_e.subtrees
