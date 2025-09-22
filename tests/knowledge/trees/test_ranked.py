from pathlib import Path
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.trees.ranked import ranked_tree

def test_ranked_tree():
    ranking = KnowledgeRanking([Path('b.txt'), Path('a/c.txt')])
    tree = ranked_tree(ranking)
    assert tree.all_paths == [Path('b.txt'), Path('a/c.txt')]
