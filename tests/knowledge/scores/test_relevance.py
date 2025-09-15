from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import coerce_subset
from llobot.knowledge.scores.relevance import PositiveRelevanceScorer, NegativeRelevanceScorer

knowledge = Knowledge({
    Path('a.txt'): '',
    Path('b.py'): '',
    Path('c.txt'): '',
    Path('d.py'): '',
})

relevant_subset = coerce_subset('*.py')
blacklist_subset = coerce_subset('d.py')

def test_positive_relevance_scorer():
    scorer = PositiveRelevanceScorer(relevant=relevant_subset, blacklist=blacklist_subset, irrelevant_weight=0.2)
    scores = scorer.score(knowledge)
    assert scores[Path('a.txt')] == 0.2
    assert scores[Path('b.py')] == 1.0
    assert scores[Path('c.txt')] == 0.2
    assert Path('d.py') not in scores

def test_negative_relevance_scorer():
    scorer = NegativeRelevanceScorer(irrelevant=relevant_subset, blacklist=blacklist_subset, irrelevant_weight=0.2)
    scores = scorer.score(knowledge)
    assert scores[Path('a.txt')] == 1.0
    assert scores[Path('b.py')] == 0.2
    assert scores[Path('c.txt')] == 1.0
    assert Path('d.py') not in scores
