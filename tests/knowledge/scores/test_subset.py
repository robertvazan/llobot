from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.scores.subset import SubsetScorer
from llobot.knowledge.subsets import coerce_subset

knowledge = Knowledge({
    PurePosixPath('a.txt'): '',
    PurePosixPath('b.py'): '',
})

def test_subset_scorer():
    subset = coerce_subset('*.py')
    scorer = SubsetScorer(subset, score=5.0)
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('b.py')] == 5.0
    assert PurePosixPath('a.txt') not in scores
