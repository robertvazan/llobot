from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.scores.length import score_length, LengthScorer

knowledge = Knowledge({
    PurePosixPath('a.txt'): 'A',
    PurePosixPath('b.txt'): 'BB',
    PurePosixPath('c.txt'): '',
})

def test_score_length():
    scores = score_length(knowledge)
    assert scores[PurePosixPath('a.txt')] == 1
    assert scores[PurePosixPath('b.txt')] == 2
    assert PurePosixPath('c.txt') not in scores

def test_length_scorer():
    scorer = LengthScorer()
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('a.txt')] == 1
    assert scores[PurePosixPath('b.txt')] == 2
    assert PurePosixPath('c.txt') not in scores
