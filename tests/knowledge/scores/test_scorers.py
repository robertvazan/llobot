from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer, coerce_scorer
from llobot.knowledge.scores.subset import SubsetScorer

knowledge = Knowledge({
    PurePosixPath('a.txt'): '',
    PurePosixPath('b.py'): '',
})

def test_knowledge_scorer_defaults():
    scorer = KnowledgeScorer()
    scores = scorer.score(knowledge)
    assert not scores

    initial = KnowledgeScores({PurePosixPath('a.txt'): 2.0})
    rescores = scorer.rescore(knowledge, initial)
    assert not rescores

def test_coerce_scorer():
    scorer = coerce_scorer('*.py')
    assert isinstance(scorer, SubsetScorer)
    scores = scorer.score(knowledge)
    assert scores[PurePosixPath('b.py')] == 1.0
    assert PurePosixPath('a.txt') not in scores

    native_scorer = KnowledgeScorer()
    assert coerce_scorer(native_scorer) is native_scorer
