from pathlib import Path
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

def test_coerce_scores_from_knowledge():
    k = Knowledge({Path('a.txt'): 'A', Path('b.txt'): 'BB'})
    scores = coerce_scores(k)
    assert scores[Path('a.txt')] == 1
    assert scores[Path('b.txt')] == 2

def test_coerce_scores_from_index():
    idx = KnowledgeIndex([Path('a.txt'), Path('b.txt')])
    scores = coerce_scores(idx)
    assert scores[Path('a.txt')] == 1
    assert scores[Path('b.txt')] == 1
