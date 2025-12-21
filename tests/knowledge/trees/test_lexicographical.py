from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.trees.lexicographical import lexicographical_tree

def test_lexicographical_tree():
    knowledge = Knowledge({PurePosixPath('b.txt'): '', PurePosixPath('a/c.txt'): ''})
    tree = lexicographical_tree(knowledge)
    assert tree.all_paths == [PurePosixPath('b.txt'), PurePosixPath('a/c.txt')]
