from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.scores.subset import SubsetScorer
from llobot.knowledge.subsets import coerce_subset

knowledge = Knowledge({
    Path('a.txt'): '',
    Path('b.py'): '',
})

def test_subset_scorer():
    subset = coerce_subset('*.py')
    scorer = SubsetScorer(subset, score=5.0)
    scores = scorer.score(knowledge)
    assert scores[Path('b.py')] == 5.0
    assert Path('a.txt') not in scores
