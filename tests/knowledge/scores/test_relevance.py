from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import coerce_subset
from llobot.knowledge.scores.relevance import PositiveRelevanceScorer, NegativeRelevanceScorer

knowledge = Knowledge({
    PurePosixPath('a.txt'): '',
    PurePosixPath('b.py'): '',
    PurePosixPath('c.txt'): '',
    PurePosixPath('d.py'): '',
})

relevant_subset = coerce_subset('*.py')
blacklist_subset = coerce_subset('d.py')

def test_positive_relevance_scorer():
    scorer = PositiveRelevanceScorer(relevant=relevant_subset, blacklist=blacklist_subset, irrelevant_weight=0.2)
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('a.txt')] == 0.2
    assert scores[PurePosixPath('b.py')] == 1.0
    assert scores[PurePosixPath('c.txt')] == 0.2
    assert PurePosixPath('d.py') not in scores

def test_negative_relevance_scorer():
    scorer = NegativeRelevanceScorer(irrelevant=relevant_subset, blacklist=blacklist_subset, irrelevant_weight=0.2)
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('a.txt')] == 1.0
    assert scores[PurePosixPath('b.py')] == 0.2
    assert scores[PurePosixPath('c.txt')] == 1.0
    assert PurePosixPath('d.py') not in scores
