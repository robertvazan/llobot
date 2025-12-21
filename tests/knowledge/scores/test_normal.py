from pathlib import PurePosixPath
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.normal import normalize_scores

def test_normalize_scores():
    scores = KnowledgeScores({PurePosixPath('a.txt'): 1.0, PurePosixPath('b.txt'): 3.0})
    normalized = normalize_scores(scores, budget=10)
    assert normalized[PurePosixPath('a.txt')] == 2.5
    assert normalized[PurePosixPath('b.txt')] == 7.5

def test_normalize_empty_scores():
    scores = KnowledgeScores()
    normalized = normalize_scores(scores)
    assert not normalized
