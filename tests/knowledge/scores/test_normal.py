from pathlib import Path
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.normal import normalize_scores

def test_normalize_scores():
    scores = KnowledgeScores({Path('a.txt'): 1.0, Path('b.txt'): 3.0})
    normalized = normalize_scores(scores, budget=10)
    assert normalized[Path('a.txt')] == 2.5
    assert normalized[Path('b.txt')] == 7.5

def test_normalize_empty_scores():
    scores = KnowledgeScores()
    normalized = normalize_scores(scores)
    assert not normalized
