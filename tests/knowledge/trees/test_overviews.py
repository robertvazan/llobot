from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.trees.overviews import overviews_first_tree

def test_overviews_first_tree():
    knowledge = Knowledge({PurePosixPath('z.txt'): '', PurePosixPath('README.md'): '', PurePosixPath('a/b.txt'): ''})
    tree = overviews_first_tree(knowledge)
    # coerce_ranking -> a/b.txt, README.md, z.txt
    # rank_overviews_first -> README.md, a/b.txt, z.txt
    # ranked_tree on that reorders to put root files first
    assert tree.all_paths == [PurePosixPath('README.md'), PurePosixPath('z.txt'), PurePosixPath('a/b.txt')]
