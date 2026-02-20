from pathlib import PurePosixPath
from typing import Any, cast
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.scores.constant import constant_scores, ConstantScorer

knowledge = Knowledge({
    PurePosixPath('a.txt'): 'A',
    PurePosixPath('b.txt'): 'BB',
})

def test_constant_scores():
    scores = constant_scores(knowledge, 2.5)
    assert scores[PurePosixPath('a.txt')] == 2.5
    assert scores[PurePosixPath('b.txt')] == 2.5
    assert PurePosixPath('c.txt') not in scores

def test_constant_scores_from_index():
    index = KnowledgeIndex([PurePosixPath('a.txt'), PurePosixPath('b.txt')])
    scores = constant_scores(index, 3.0)
    assert scores[PurePosixPath('a.txt')] == 3.0
    assert scores[PurePosixPath('b.txt')] == 3.0
    assert PurePosixPath('c.txt') not in scores

def test_constant_scorer():
    scorer = ConstantScorer(3.0)
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('a.txt')] == 3.0
    assert scores[PurePosixPath('b.txt')] == 3.0
    assert PurePosixPath('c.txt') not in scores

def test_constant_scorer_default():
    scorer = ConstantScorer()
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('a.txt')] == 1.0
    assert scores[PurePosixPath('b.txt')] == 1.0

def test_constant_scores_invalid_type():
    from llobot.knowledge.scores import KnowledgeScores
    try:
        constant_scores(cast(Any, KnowledgeScores({PurePosixPath('a.txt'): 1.0})))
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
