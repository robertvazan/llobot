from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker, rank_lexicographically

PATHS = [
    Path('z.txt'),
    Path('a/z.txt'),
    Path('a/b.txt'),
]
KNOWLEDGE_INDEX = KnowledgeIndex(PATHS)
KNOWLEDGE = Knowledge({p: '' for p in PATHS})
EXPECTED = KnowledgeRanking([
    Path('a/b.txt'),
    Path('a/z.txt'),
    Path('z.txt'),
])

def test_rank_lexicographically():
    ranking = rank_lexicographically(KNOWLEDGE_INDEX)
    assert ranking == EXPECTED

def test_lexicographical_ranker():
    ranker = LexicographicalRanker()
    ranking = ranker.rank(KNOWLEDGE)
    assert ranking == EXPECTED
    # Test value semantics
    assert ranker == LexicographicalRanker()
    assert hash(ranker) == hash(LexicographicalRanker())
