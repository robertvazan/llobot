from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.sorting import AscendingRanker, DescendingRanker, rank_ascending, rank_descending
from llobot.knowledge.ranking.trees import PreorderRanker
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer, standard_scorer
from llobot.utils.values import ValueTypeMixin

SCORES = KnowledgeScores({
    PurePosixPath('a.txt'): 10,
    PurePosixPath('b.txt'): 30,
    PurePosixPath('c.txt'): 20,
})
KNOWLEDGE = Knowledge({p: '' for p in SCORES.keys()})

class MockScorer(KnowledgeScorer, ValueTypeMixin):
    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        return SCORES

def test_rank_ascending_no_initial():
    ranking = rank_ascending(SCORES)
    assert ranking == KnowledgeRanking([PurePosixPath('a.txt'), PurePosixPath('c.txt'), PurePosixPath('b.txt')])

def test_rank_descending_no_initial():
    ranking = rank_descending(SCORES)
    assert ranking == KnowledgeRanking([PurePosixPath('b.txt'), PurePosixPath('c.txt'), PurePosixPath('a.txt')])

def test_rank_ascending_with_initial():
    initial = KnowledgeRanking([PurePosixPath('c.txt'), PurePosixPath('b.txt'), PurePosixPath('a.txt')])
    ranking = rank_ascending(SCORES, initial=initial)
    assert ranking == KnowledgeRanking([PurePosixPath('a.txt'), PurePosixPath('c.txt'), PurePosixPath('b.txt')])

def test_rank_descending_with_initial():
    initial = KnowledgeRanking([PurePosixPath('c.txt'), PurePosixPath('b.txt'), PurePosixPath('a.txt')])
    ranking = rank_descending(SCORES, initial=initial)
    assert ranking == KnowledgeRanking([PurePosixPath('b.txt'), PurePosixPath('c.txt'), PurePosixPath('a.txt')])

def test_rank_ascending_stable_sort():
    scores = KnowledgeScores({PurePosixPath('a.txt'): 10, PurePosixPath('b.txt'): 20, PurePosixPath('c.txt'): 10})
    initial = KnowledgeRanking([PurePosixPath('c.txt'), PurePosixPath('a.txt'), PurePosixPath('b.txt')])
    ranking = rank_ascending(scores, initial=initial)
    # c.txt comes before a.txt in initial, so it should be first among equals
    assert ranking == KnowledgeRanking([PurePosixPath('c.txt'), PurePosixPath('a.txt'), PurePosixPath('b.txt')])

def test_ascending_ranker():
    ranker = AscendingRanker(scorer=MockScorer(), tiebreaker=LexicographicalRanker())
    ranking = ranker.rank(KNOWLEDGE)
    assert ranking == KnowledgeRanking([PurePosixPath('a.txt'), PurePosixPath('c.txt'), PurePosixPath('b.txt')])
    # Test value semantics
    default_tiebreaker = PreorderRanker(tiebreaker=LexicographicalRanker())
    assert AscendingRanker(scorer=MockScorer()) == AscendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker)
    assert hash(AscendingRanker(scorer=MockScorer())) == hash(AscendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker))
    # Test default scorer
    assert AscendingRanker()._scorer == standard_scorer()

def test_descending_ranker():
    ranker = DescendingRanker(scorer=MockScorer(), tiebreaker=LexicographicalRanker())
    ranking = ranker.rank(KNOWLEDGE)
    assert ranking == KnowledgeRanking([PurePosixPath('b.txt'), PurePosixPath('c.txt'), PurePosixPath('a.txt')])
    # Test value semantics
    default_tiebreaker = PreorderRanker(tiebreaker=LexicographicalRanker())
    assert DescendingRanker(scorer=MockScorer()) == DescendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker)
    assert hash(DescendingRanker(scorer=MockScorer())) == hash(DescendingRanker(scorer=MockScorer(), tiebreaker=default_tiebreaker))
    # Test default scorer
    assert DescendingRanker()._scorer == standard_scorer()
