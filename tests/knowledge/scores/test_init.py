from pathlib import PurePosixPath
from unittest.mock import patch
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores, coerce_scores
from llobot.knowledge.indexes import KnowledgeIndex

def test_knowledge_scores():
    scores = KnowledgeScores({PurePosixPath('a.txt'): 1.0, PurePosixPath('b.txt'): 2.0, PurePosixPath('c.txt'): 0})
    assert len(scores) == 2
    assert PurePosixPath('a.txt') in scores
    assert PurePosixPath('b.txt') in scores
    assert PurePosixPath('c.txt') not in scores
    assert scores[PurePosixPath('a.txt')] == 1.0
    assert scores[PurePosixPath('b.txt')] == 2.0
    assert scores[PurePosixPath('d.txt')] == 0.0
    assert scores.total() == 3.0

@patch('llobot.knowledge.scores.scorers.standard_scorer')
def test_coerce_scores_from_knowledge(mock_standard_scorer):
    mock_scorer = mock_standard_scorer.return_value
    mock_scorer.score.return_value = KnowledgeScores({PurePosixPath('a.txt'): 10.0, PurePosixPath('b.txt'): 20.0})

    k = Knowledge({PurePosixPath('a.txt'): 'A', PurePosixPath('b.txt'): 'BB'})
    scores = coerce_scores(k)
    assert scores == KnowledgeScores({PurePosixPath('a.txt'): 10.0, PurePosixPath('b.txt'): 20.0})

    mock_standard_scorer.assert_called_once_with()
    mock_scorer.score.assert_called_once_with(k)

def test_coerce_scores_from_index():
    idx = KnowledgeIndex([PurePosixPath('a.txt'), PurePosixPath('b.txt')])
    scores = coerce_scores(idx)
    assert scores[PurePosixPath('a.txt')] == 1
    assert scores[PurePosixPath('b.txt')] == 1
