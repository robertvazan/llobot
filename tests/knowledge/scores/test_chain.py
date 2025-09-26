from pathlib import Path
from unittest.mock import Mock
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.chain import KnowledgeScorerChain
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.knowledge.scores.constant import ConstantScorer

knowledge = Knowledge({Path('a.txt'): 'A', Path('b.txt'): 'BB'})

def test_chain_empty():
    chain = KnowledgeScorerChain()
    scores = chain.score(knowledge)
    assert scores[Path('a.txt')] == 1
    assert scores[Path('b.txt')] == 1

    initial = KnowledgeScores({Path('a.txt'): 10})
    rescores = chain.rescore(knowledge, initial)
    assert rescores is initial

def test_chain_score():
    scorer1 = Mock(spec=KnowledgeScorer)
    scorer1.score.return_value = KnowledgeScores({Path('a.txt'): 10, Path('b.txt'): 20})
    scorer2 = Mock(spec=KnowledgeScorer)
    scorer2.rescore.return_value = KnowledgeScores({Path('a.txt'): 5, Path('b.txt'): 15})
    chain = KnowledgeScorerChain(scorer1, scorer2)
    scores = chain.score(knowledge)
    assert scores == KnowledgeScores({Path('a.txt'): 5, Path('b.txt'): 15})
    scorer1.score.assert_called_once_with(knowledge)
    scorer2.rescore.assert_called_once_with(knowledge, KnowledgeScores({Path('a.txt'): 10, Path('b.txt'): 20}))

def test_chain_rescore():
    scorer1 = Mock(spec=KnowledgeScorer)
    scorer1.rescore.return_value = KnowledgeScores({Path('a.txt'): 10, Path('b.txt'): 20})
    scorer2 = Mock(spec=KnowledgeScorer)
    scorer2.rescore.return_value = KnowledgeScores({Path('a.txt'): 5, Path('b.txt'): 15})
    chain = KnowledgeScorerChain(scorer1, scorer2)
    initial = KnowledgeScores({Path('a.txt'): 1})
    scores = chain.rescore(knowledge, initial)
    assert scores == KnowledgeScores({Path('a.txt'): 5, Path('b.txt'): 15})
    scorer1.rescore.assert_called_once_with(knowledge, initial)
    scorer2.rescore.assert_called_once_with(knowledge, KnowledgeScores({Path('a.txt'): 10, Path('b.txt'): 20}))

def test_chain_flattening():
    scorer1 = ConstantScorer(1)
    scorer2 = ConstantScorer(2)
    scorer3 = ConstantScorer(3)
    chain1 = KnowledgeScorerChain(scorer1, scorer2)
    chain2 = KnowledgeScorerChain(chain1, scorer3)
    assert chain2._scorers == (scorer1, scorer2, scorer3)

def test_or_operator():
    scorer1 = ConstantScorer(1)
    scorer2 = ConstantScorer(2)
    chain = scorer1 | scorer2
    assert isinstance(chain, KnowledgeScorerChain)
    assert chain._scorers == (scorer1, scorer2)
