from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.scores.random import random_scores, RandomScorer

knowledge = Knowledge({
    Path('a.txt'): 'A',
    Path('b.txt'): 'BB',
})

def test_random_scores():
    scores1 = random_scores(knowledge)
    scores2 = random_scores(knowledge)
    assert scores1 == scores2
    assert len(scores1) == 2
    assert scores1[Path('a.txt')] != scores1[Path('b.txt')]

def test_random_scorer():
    scorer = RandomScorer()
    scores = scorer.score(knowledge)
    assert len(scores) == 2
    assert scores[Path('a.txt')] != 0
    assert scores[Path('b.txt')] != 0
