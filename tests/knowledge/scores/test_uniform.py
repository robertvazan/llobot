from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.scores.uniform import uniform_scores, UniformScorer

knowledge = Knowledge({
    Path('a.txt'): 'A',
    Path('b.txt'): 'BB',
    Path('c.txt'): 'CCC',
})

def test_uniform_scores():
    scores = uniform_scores(knowledge, 12.0)
    assert scores[Path('a.txt')] == 4.0
    assert scores[Path('b.txt')] == 4.0
    assert scores[Path('c.txt')] == 4.0

def test_uniform_scores_from_index():
    index = KnowledgeIndex([Path('a.txt'), Path('b.txt')])
    scores = uniform_scores(index, 10.0)
    assert scores[Path('a.txt')] == 5.0
    assert scores[Path('b.txt')] == 5.0

def test_uniform_scorer():
    scorer = UniformScorer(6.0)
    scores = scorer.score(knowledge)
    assert scores[Path('a.txt')] == 2.0
    assert scores[Path('b.txt')] == 2.0
    assert scores[Path('c.txt')] == 2.0

def test_uniform_scorer_default():
    scorer = UniformScorer()
    scores = scorer.score(knowledge)
    assert round(scores.total(), 5) == 1.0

def test_uniform_scores_invalid_type():
    from llobot.knowledge.scores import KnowledgeScores
    try:
        uniform_scores(KnowledgeScores({Path('a.txt'): 1.0}))
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
