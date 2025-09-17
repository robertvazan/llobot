from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.ranking.trees import PreorderRanker, preorder_ranking
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

def test_preorder_ranker():
    knowledge = Knowledge({
        Path('d1/f2'): '',
        Path('f1'): '',
        Path('d2/f3'): '',
    })
    # Initial ranking from LexicographicalRanker will be f1, d1/f2, d2/f3
    ranker = PreorderRanker(previous=LexicographicalRanker())
    ranking = ranker.rank(knowledge)
    # The tree built from lex order is: f1, then d1 dir with f2, then d2 dir with f3.
    # Preorder traversal is f1, d1/f2, d2/f3.
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d1/f2'),
        Path('d2/f3'),
    ])

    # Test with a different previous ranker that reverses order.
    class ReversedLexRanker(KnowledgeRanker):
        def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
            return LexicographicalRanker().rank(knowledge).reversed()

    # Initial ranking: d2/f3, d1/f2, f1.
    # Tree: d2 dir with f3, then d1 dir with f2, then f1.
    # Tree files: ['f1']. Subdirs: ['d2', 'd1']. d2 has files ['f3']. d1 has files ['f2'].
    # Preorder traversal: f1, d2/f3, d1/f2.
    ranker = PreorderRanker(previous=ReversedLexRanker())
    ranking = ranker.rank(knowledge)
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d2/f3'),
        Path('d1/f2'),
    ])

    # test value semantics
    assert PreorderRanker() == PreorderRanker()
    assert hash(PreorderRanker()) == hash(PreorderRanker())
