from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.trees.lexicographical import lexicographical_tree

def test_lexicographical_tree():
    knowledge = Knowledge({Path('b.txt'): '', Path('a/c.txt'): ''})
    tree = lexicographical_tree(knowledge)
    assert tree.all_paths == [Path('b.txt'), Path('a/c.txt')]
