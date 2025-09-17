from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking, coerce_ranking, standard_ranking

PATHS = [
    Path('a/b/c.txt'),
    Path('a/b/__init__.py'),
    Path('a/README.md'),
    Path('main.py'),
    Path('README.md'),
]
KNOWLEDGE = Knowledge({p: '' for p in PATHS})
KNOWLEDGE_INDEX = KnowledgeIndex(PATHS)

def test_coerce_ranking_from_ranking():
    ranking = KnowledgeRanking(PATHS)
    assert coerce_ranking(ranking) is ranking

def test_coerce_ranking_from_iterable():
    ranking = coerce_ranking(PATHS)
    assert isinstance(ranking, KnowledgeRanking)
    assert ranking._paths == PATHS

def test_coerce_ranking_from_knowledge():
    ranking = coerce_ranking(KNOWLEDGE)
    assert ranking == KnowledgeRanking(sorted(PATHS))

def test_coerce_ranking_from_index():
    ranking = coerce_ranking(KNOWLEDGE_INDEX)
    assert ranking == KnowledgeRanking(sorted(PATHS))

def test_standard_ranking_from_index():
    ranking = standard_ranking(KNOWLEDGE_INDEX)
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('main.py'),
        Path('a/README.md'),
        Path('a/b/__init__.py'),
        Path('a/b/c.txt'),
    ])

def test_standard_ranking_from_knowledge():
    ranking = standard_ranking(KNOWLEDGE)
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('main.py'),
        Path('a/README.md'),
        Path('a/b/__init__.py'),
        Path('a/b/c.txt'),
    ])
