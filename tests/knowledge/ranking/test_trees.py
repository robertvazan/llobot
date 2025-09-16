from pathlib import Path
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.trees import preorder_ranking
from llobot.knowledge.trees import KnowledgeTree, ranked_tree

def test_preorder_ranking_from_tree():
    tree = KnowledgeTree(
        files=['f1'],
        subtrees=[
            KnowledgeTree('d1', files=['f2']),
            KnowledgeTree('d2', files=['f3']),
        ]
    )
    ranking = preorder_ranking(tree)
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d1/f2'),
        Path('d2/f3'),
    ])

def test_preorder_ranking_from_ranking():
    initial = KnowledgeRanking([Path('d1/f2'), Path('f1'), Path('d2/f3')])
    ranking = preorder_ranking(initial)
    # The order is determined by the tree structure, not initial ranking order
    tree = ranked_tree(initial)
    assert tree.files == ['f1']
    assert [st.base.name for st in tree.subtrees] == ['d1', 'd2']
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d1/f2'),
        Path('d2/f3'),
    ])
