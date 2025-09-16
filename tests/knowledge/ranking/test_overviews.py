from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.overviews import (
    OverviewsBeforeSiblingsRanker,
    rank_overviews_before_document,
    rank_overviews_before_everything,
    rank_overviews_before_siblings,
)
from llobot.knowledge.subsets.filename import FilenameSubset
from llobot.knowledge.subsets.standard import overviews_subset

PATHS = KnowledgeRanking([
    Path('README.md'),
    Path('a/doc.txt'),
    Path('a/README.md'),
    Path('a/b/script.py'),
    Path('a/b/README.md'),
])
OVERVIEWS = FilenameSubset('README.md')

def test_rank_overviews_before_everything():
    ranking = rank_overviews_before_everything(PATHS, overviews=OVERVIEWS)
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('a/README.md'),
        Path('a/b/README.md'),
        Path('a/doc.txt'),
        Path('a/b/script.py'),
    ])

def test_rank_overviews_before_siblings():
    ranking = rank_overviews_before_siblings(PATHS, overviews=OVERVIEWS)
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('a/README.md'),
        Path('a/doc.txt'),
        Path('a/b/README.md'),
        Path('a/b/script.py'),
    ])

def test_rank_overviews_before_document():
    ranking = rank_overviews_before_document(PATHS, overviews=OVERVIEWS)
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('a/README.md'),
        Path('a/doc.txt'),
        Path('a/b/README.md'),
        Path('a/b/script.py'),
    ])

def test_rank_overviews_before_document_root_overview():
    initial = KnowledgeRanking([Path('a/b/c.txt'), Path('README.md')])
    overviews = FilenameSubset('README.md')
    ranking = rank_overviews_before_document(initial, overviews=overviews)
    assert ranking == KnowledgeRanking([Path('README.md'), Path('a/b/c.txt')])

def test_overviews_before_siblings_ranker():
    ranker = OverviewsBeforeSiblingsRanker(previous=LexicographicalRanker(), overviews=OVERVIEWS)
    knowledge = Knowledge({
        Path('a/doc.txt'): '',
        Path('a/b/script.py'): '',
        Path('README.md'): '',
        Path('a/README.md'): '',
        Path('a/b/README.md'): '',
    })
    ranking = ranker.rank(knowledge)
    # Lexicographical order first, then overviews are moved.
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('a/README.md'),
        Path('a/doc.txt'),
        Path('a/b/README.md'),
        Path('a/b/script.py'),
    ])
    # Test value semantics
    assert ranker == OverviewsBeforeSiblingsRanker(previous=LexicographicalRanker(), overviews=OVERVIEWS)
    assert hash(ranker) == hash(OverviewsBeforeSiblingsRanker(previous=LexicographicalRanker(), overviews=OVERVIEWS))
    assert ranker != OverviewsBeforeSiblingsRanker(previous=LexicographicalRanker())
    # Test default overviews
    ranker_default = OverviewsBeforeSiblingsRanker()
    assert ranker_default._overviews == overviews_subset()
