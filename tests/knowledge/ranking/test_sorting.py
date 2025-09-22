from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.sorting import AscendingRanker, DescendingRanker, rank_ascending, rank_descending
from llobot.knowledge.ranking.trees import PreorderRanker
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer, standard_scorer
from llobot.utils.values import ValueTypeMixin

SCORES = KnowledgeScores({
    Path('a.txt'): 10,
    Path('b.txt'): 30,
    Path('c.txt'): 20,
})
KNOWLEDGE = Knowledge({p: '' for p in SCORES.keys()})

class MockScorer(KnowledgeScorer, ValueTypeMixin):
    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        return SCORES

def test_rank_ascending_no_initial():
    ranking = rank_ascending(SCORES)
    assert ranking == KnowledgeRanking([Path('a.txt'), Path('c.txt'), Path('b.txt')])

def test_rank_descending_no_initial():
    ranking = rank_descending(SCORES)
    assert ranking == KnowledgeRanking([Path('b.txt'), Path('c.txt'), Path('a.txt')])

def test_rank_ascending_with_initial():
    initial = KnowledgeRanking([Path('c.txt'), Path('b.txt'), Path('a.txt')])
    ranking = rank_ascending(SCORES, initial=initial)
    assert ranking == KnowledgeRanking([Path('a.txt'), Path('c.txt'), Path('b.txt')])

def test_rank_descending_with_initial():
    initial = KnowledgeRanking([Path('c.txt'), Path('b.txt'), Path('a.txt')])
    ranking = rank_descending(SCORES, initial=initial)
    assert ranking == KnowledgeRanking([Path('b.txt'), Path('c.txt'), Path('a.txt')])

def test_rank_ascending_stable_sort():
    scores = KnowledgeScores({Path('a.txt'): 10, Path('b.txt'): 20, Path('c.txt'): 10})
    initial = KnowledgeRanking([Path('c.txt'), Path('a.txt'), Path('b.txt')])
    ranking = rank_ascending(scores, initial=initial)
    # c.txt comes before a.txt in initial, so it should be first among equals
    assert ranking == KnowledgeRanking([Path('c.txt'), Path('a.txt'), Path('b.txt')])

def test_ascending_ranker():
    ranker = AscendingRanker(scorer=MockScorer(), tiebreaker=LexicographicalRanker())
    ranking = ranker.rank(KNOWLEDGE)
    assert ranking == KnowledgeRanking([Path('a.txt'), Path('c.txt'), Path('b.txt')])
    # Test value semantics
    default_tiebreaker = PreorderRanker(tiebreaker=LexicographicalRanker())
    assert AscendingRanker(scorer=MockScorer()) == AscendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker)
    assert hash(AscendingRanker(scorer=MockScorer())) == hash(AscendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker))
    # Test default scorer
    assert AscendingRanker()._scorer == standard_scorer()

def test_descending_ranker():
    ranker = DescendingRanker(scorer=MockScorer(), tiebreaker=LexicographicalRanker())
    ranking = ranker.rank(KNOWLEDGE)
    assert ranking == KnowledgeRanking([Path('b.txt'), Path('c.txt'), Path('a.txt')])
    # Test value semantics
    default_tiebreaker = PreorderRanker(tiebreaker=LexicographicalRanker())
    assert DescendingRanker(scorer=MockScorer()) == DescendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker)
    assert hash(DescendingRanker(scorer=MockScorer())) == hash(DescendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker))
    # Test default scorer
    assert DescendingRanker()._scorer == standard_scorer()
