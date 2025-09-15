from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.pagerank import PageRankScorer
from llobot.scrapers import create_scraper

p = lambda s: Path(s)

def test_pagerank_scorer_hub():
    knowledge = Knowledge({p('a'): '', p('b'): '', p('c'): ''})
    graph = KnowledgeGraph({
        p('a'): KnowledgeIndex([p('c')]),
        p('b'): KnowledgeIndex([p('c')]),
    })
    scraper = create_scraper(lambda k: graph)
    scorer = PageRankScorer(scraper)
    scores = scorer.score(knowledge)
    assert len(scores) == 3
    assert scores[p('c')] > scores[p('a')]
    assert scores[p('c')] > scores[p('b')]
    assert scores[p('a')] == scores[p('b')]

def test_pagerank_scorer_authority():
    knowledge = Knowledge({p('a'): '', p('b'): '', p('c'): ''})
    graph = KnowledgeGraph({
        p('a'): KnowledgeIndex([p('b'), p('c')]),
    })
    scraper = create_scraper(lambda k: graph)
    scorer = PageRankScorer(scraper)
    scores = scorer.score(knowledge)
    assert len(scores) == 3
    assert scores[p('b')] > scores[p('a')]
    assert scores[p('c')] > scores[p('a')]
    assert scores[p('b')] == scores[p('c')]

def test_pagerank_rescore():
    knowledge = Knowledge({p('a'): '', p('b'): ''})
    graph = KnowledgeGraph({
        p('a'): KnowledgeIndex([p('b')]),
    })
    scraper = create_scraper(lambda k: graph)
    scorer = PageRankScorer(scraper)
    initial = KnowledgeScores({p('a'): 10.0, p('b'): 1.0})
    scores = scorer.rescore(knowledge, initial)
    assert len(scores) == 2
    assert scores[p('a')] > scores[p('b')]
