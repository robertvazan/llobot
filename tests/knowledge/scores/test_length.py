from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.scores.length import score_length, LengthScorer

knowledge = Knowledge({
    Path('a.txt'): 'A',
    Path('b.txt'): 'BB',
    Path('c.txt'): '',
})

def test_score_length():
    scores = score_length(knowledge)
    assert scores[Path('a.txt')] == 1
    assert scores[Path('b.txt')] == 2
    assert Path('c.txt') not in scores

def test_length_scorer():
    scorer = LengthScorer()
    scores = scorer.score(knowledge)
    assert scores[Path('a.txt')] == 1
    assert scores[Path('b.txt')] == 2
    assert Path('c.txt') not in scores
