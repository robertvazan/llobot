from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer, coerce_scorer
from llobot.knowledge.scores.subset import SubsetScorer

knowledge = Knowledge({
    Path('a.txt'): '',
    Path('b.py'): '',
})

def test_knowledge_scorer_defaults():
    scorer = KnowledgeScorer()
    scores = scorer.score(knowledge)
    assert not scores

    initial = KnowledgeScores({Path('a.txt'): 2.0})
    rescores = scorer.rescore(knowledge, initial)
    assert not rescores

def test_coerce_scorer():
    scorer = coerce_scorer('*.py')
    assert isinstance(scorer, SubsetScorer)
    scores = scorer.score(knowledge)
    assert scores[Path('b.py')] == 1.0
    assert Path('a.txt') not in scores

    native_scorer = KnowledgeScorer()
    assert coerce_scorer(native_scorer) is native_scorer
