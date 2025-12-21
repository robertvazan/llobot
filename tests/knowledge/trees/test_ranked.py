from pathlib import PurePosixPath
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.trees.ranked import ranked_tree

def test_ranked_tree():
    ranking = KnowledgeRanking([PurePosixPath('b.txt'), PurePosixPath('a/c.txt')])
    tree = ranked_tree(ranking)
    assert tree.all_paths == [PurePosixPath('b.txt'), PurePosixPath('a/c.txt')]
