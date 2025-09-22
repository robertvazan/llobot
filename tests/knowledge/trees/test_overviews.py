from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.trees.overviews import overviews_first_tree

def test_overviews_first_tree():
    knowledge = Knowledge({Path('z.txt'): '', Path('README.md'): '', Path('a/b.txt'): ''})
    tree = overviews_first_tree(knowledge)
    # overviews from anywhere are first
    # coerce_ranking -> a/b.txt, README.md, z.txt
    # rank_overviews_before_everything -> README.md, a/b.txt, z.txt
    # ranked_tree on that reorders to put root files first
    assert tree.all_paths == [Path('README.md'), Path('z.txt'), Path('a/b.txt')]
