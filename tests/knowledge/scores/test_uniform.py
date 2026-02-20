from pathlib import PurePosixPath
from typing import Any, cast
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.scores.uniform import uniform_scores, UniformScorer

knowledge = Knowledge({
    PurePosixPath('a.txt'): 'A',
    PurePosixPath('b.txt'): 'BB',
    PurePosixPath('c.txt'): 'CCC',
})

def test_uniform_scores():
    scores = uniform_scores(knowledge, 12.0)
    assert scores[PurePosixPath('a.txt')] == 4.0
    assert scores[PurePosixPath('b.txt')] == 4.0
    assert scores[PurePosixPath('c.txt')] == 4.0

def test_uniform_scores_from_index():
    index = KnowledgeIndex([PurePosixPath('a.txt'), PurePosixPath('b.txt')])
    scores = uniform_scores(index, 10.0)
    assert scores[PurePosixPath('a.txt')] == 5.0
    assert scores[PurePosixPath('b.txt')] == 5.0

def test_uniform_scorer():
    scorer = UniformScorer(6.0)
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('a.txt')] == 2.0
    assert scores[PurePosixPath('b.txt')] == 2.0
    assert scores[PurePosixPath('c.txt')] == 2.0

def test_uniform_scorer_default():
    scorer = UniformScorer()
    scores = scorer.score(knowledge)
    assert round(scores.total(), 5) == 1.0

def test_uniform_scores_invalid_type():
    from llobot.knowledge.scores import KnowledgeScores
    try:
        uniform_scores(cast(Any, KnowledgeScores({PurePosixPath('a.txt'): 1.0})))
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
