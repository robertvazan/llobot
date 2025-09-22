from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.ranking.overviews import (
    OverviewsFirstRanker,
    rank_overviews_first,
)
from llobot.knowledge.ranking.trees import PreorderRanker
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
KNOWLEDGE = Knowledge({
    Path('a/doc.txt'): '',
    Path('a/b/script.py'): '',
    Path('README.md'): '',
    Path('a/README.md'): '',
    Path('a/b/README.md'): '',
})

def test_rank_overviews_first():
    ranking = rank_overviews_first(PATHS, overviews=OVERVIEWS)
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('a/README.md'),
        Path('a/doc.txt'),
        Path('a/b/README.md'),
        Path('a/b/script.py'),
    ])

def test_rank_overviews_first_root_overview():
    initial = KnowledgeRanking([Path('a/b/c.txt'), Path('README.md')])
    overviews = FilenameSubset('README.md')
    ranking = rank_overviews_first(initial, overviews=overviews)
    assert ranking == KnowledgeRanking([Path('README.md'), Path('a/b/c.txt')])

def test_overviews_first_ranker():
    ranker = OverviewsFirstRanker(tiebreaker=LexicographicalRanker(), overviews=OVERVIEWS)
    ranking = ranker.rank(KNOWLEDGE)
    # Lexicographical order first, then overviews are moved.
    assert ranking == KnowledgeRanking([
        Path('README.md'),
        Path('a/README.md'),
        Path('a/b/README.md'),
        Path('a/b/script.py'),
        Path('a/doc.txt'),
    ])
    # Test value semantics
    default_tiebreaker = PreorderRanker(tiebreaker=LexicographicalRanker())
    assert OverviewsFirstRanker(overviews=OVERVIEWS) == OverviewsFirstRanker(tiebreaker=default_tiebreaker, overviews=OVERVIEWS)
    assert hash(OverviewsFirstRanker(overviews=OVERVIEWS)) == hash(OverviewsFirstRanker(tiebreaker=default_tiebreaker, overviews=OVERVIEWS))
    assert OverviewsFirstRanker(overviews=OVERVIEWS) != OverviewsFirstRanker(tiebreaker=LexicographicalRanker(), overviews=OVERVIEWS)
    # Test default overviews
    ranker_default = OverviewsFirstRanker()
    assert ranker_default._overviews == overviews_subset()
