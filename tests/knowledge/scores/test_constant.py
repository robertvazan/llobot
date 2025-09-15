from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.scores.constant import constant_scores, ConstantScorer

knowledge = Knowledge({
    Path('a.txt'): 'A',
    Path('b.txt'): 'BB',
})

def test_constant_scores():
    scores = constant_scores(knowledge, 2.5)
    assert scores[Path('a.txt')] == 2.5
    assert scores[Path('b.txt')] == 2.5
    assert Path('c.txt') not in scores

def test_constant_scorer():
    scorer = ConstantScorer(3.0)
    scores = scorer.score(knowledge)
    assert scores[Path('a.txt')] == 3.0
    assert scores[Path('b.txt')] == 3.0
    assert Path('c.txt') not in scores

def test_constant_scorer_default():
    scorer = ConstantScorer()
    scores = scorer.score(knowledge)
    assert scores[Path('a.txt')] == 1.0
    assert scores[Path('b.txt')] == 1.0
