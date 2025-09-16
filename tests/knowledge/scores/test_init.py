from pathlib import Path
from unittest.mock import patch
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores, coerce_scores
from llobot.knowledge.indexes import KnowledgeIndex

def test_knowledge_scores():
    scores = KnowledgeScores({Path('a.txt'): 1.0, Path('b.txt'): 2.0, Path('c.txt'): 0})
    assert len(scores) == 2
    assert Path('a.txt') in scores
    assert Path('b.txt') in scores
    assert Path('c.txt') not in scores
    assert scores[Path('a.txt')] == 1.0
    assert scores[Path('b.txt')] == 2.0
    assert scores[Path('d.txt')] == 0.0
    assert scores.total() == 3.0

@patch('llobot.knowledge.scores.scorers.standard_scorer')
def test_coerce_scores_from_knowledge(mock_standard_scorer):
    mock_scorer = mock_standard_scorer.return_value
    mock_scorer.score.return_value = KnowledgeScores({Path('a.txt'): 10.0, Path('b.txt'): 20.0})

    k = Knowledge({Path('a.txt'): 'A', Path('b.txt'): 'BB'})
    scores = coerce_scores(k)
    assert scores == KnowledgeScores({Path('a.txt'): 10.0, Path('b.txt'): 20.0})

    mock_standard_scorer.assert_called_once_with()
    mock_scorer.score.assert_called_once_with(k)

def test_coerce_scores_from_index():
    idx = KnowledgeIndex([Path('a.txt'), Path('b.txt')])
    scores = coerce_scores(idx)
    assert scores[Path('a.txt')] == 1
    assert scores[Path('b.txt')] == 1
