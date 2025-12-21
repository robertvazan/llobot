from pathlib import PurePosixPath
from llobot.knowledge.trees.builder import KnowledgeTreeBuilder

def test_builder():
    builder = KnowledgeTreeBuilder()
    builder.add('a/b.txt')
    builder.add('a/c.txt')
    builder.add('d.txt')
    builder.add('a/e/f.txt')
    tree = builder.build()

    assert tree.base == PurePosixPath('.')
    assert tree.files == ['d.txt']
    assert len(tree.subtrees) == 1

    subtree_a = tree.subtrees[0]
    assert subtree_a.base == PurePosixPath('a')
    assert subtree_a.files == ['b.txt', 'c.txt']
    assert len(subtree_a.subtrees) == 1

    subtree_e = subtree_a.subtrees[0]
    assert subtree_e.base == PurePosixPath('a/e')
    assert subtree_e.files == ['f.txt']
    assert not subtree_e.subtrees
