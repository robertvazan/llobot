from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.knowledge.ranking.trees import PreorderRanker, preorder_lexicographical_ranking, preorder_ranking
from llobot.knowledge.trees import KnowledgeTree
from llobot.knowledge.trees.ranked import ranked_tree

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
    # The tree-based reordering places root files before subdirectory files.
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d1/f2'),
        Path('d2/f3'),
    ])

def test_preorder_lexicographical_ranking():
    index = KnowledgeIndex([Path('d1/f2'), Path('f1'), Path('d2/f3')])
    ranking = preorder_lexicographical_ranking(index)
    # Lexicographical sort first: d1/f2, d2/f3, f1.
    # Tree from that: d1/ with f2, d2/ with f3, then f1.
    # Preorder traversal of the tree: f1, d1/f2, d2/f3.
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
    # Initial ranking from LexicographicalRanker will be d1/f2, d2/f3, f1.
    ranker = PreorderRanker(tiebreaker=LexicographicalRanker())
    ranking = ranker.rank(knowledge)
    # The tree built from lex order is: d1 dir with f2, then d2 dir with f3, then f1.
    # Preorder traversal is f1, d1/f2, d2/f3.
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d1/f2'),
        Path('d2/f3'),
    ])

    # Test with a different tiebreaker ranker that reverses order.
    class ReversedLexRanker(KnowledgeRanker):
        def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
            return LexicographicalRanker().rank(knowledge).reversed()

    # Initial ranking: f1, d2/f3, d1/f2.
    ranker = PreorderRanker(tiebreaker=ReversedLexRanker())
    ranking = ranker.rank(knowledge)
    # Tree built from reversed lex order.
    # ranked_tree(['f1', 'd2/f3', 'd1/f2'])
    # Preorder traversal: f1, d2/f3, d1/f2.
    assert ranking == KnowledgeRanking([
        Path('f1'),
        Path('d2/f3'),
        Path('d1/f2'),
    ])

    # test value semantics
    assert PreorderRanker() == PreorderRanker()
    assert hash(PreorderRanker()) == hash(PreorderRanker())
