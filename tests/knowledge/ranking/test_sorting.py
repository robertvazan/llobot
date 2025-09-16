from pathlib import Path
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.sorting import rank_ascending, rank_descending
from llobot.knowledge.scores import KnowledgeScores

SCORES = KnowledgeScores({
    Path('a.txt'): 10,
    Path('b.txt'): 30,
    Path('c.txt'): 20,
})

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
