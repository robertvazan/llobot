from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.scrapers.index import ScrapingIndex, create_scraping_index

def test_scraping_index_creation():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/test_main.py'),
        Path('README.md'),
    ])
    scraping_index = ScrapingIndex(index)
    
    # Test names mapping
    assert Path('src/main.py') in scraping_index._names['main.py']
    assert Path('test/test_main.py') in scraping_index._names['test_main.py']
    assert Path('README.md') in scraping_index._names['README.md']
    
    # Test tails mapping
    assert Path('src/utils/helper.py') in scraping_index._tails[Path('utils/helper.py')]

def test_create_scraping_index_from_knowledge():
    knowledge = Knowledge({
        Path('src/main.py'): 'content',
        Path('README.md'): 'content',
    })
    scraping_index = create_scraping_index(knowledge)
    assert isinstance(scraping_index, ScrapingIndex)

def test_create_scraping_index_from_index():
    index = KnowledgeIndex([Path('src/main.py'), Path('README.md')])
    scraping_index = create_scraping_index(index)
    assert isinstance(scraping_index, ScrapingIndex)

def test_create_scraping_index_from_ranking():
    ranking = KnowledgeRanking([Path('src/main.py'), Path('README.md')])
    scraping_index = create_scraping_index(ranking)
    assert isinstance(scraping_index, ScrapingIndex)

def test_create_scraping_index_invalid_type():
    from llobot.knowledge.scores import KnowledgeScores
    try:
        create_scraping_index(KnowledgeScores({Path('a.txt'): 1.0}))
        assert False, "Should have raised TypeError"
    except TypeError:
        pass

def test_scraping_index_lookup():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/main.py'),
    ])
    scraping_index = ScrapingIndex(index)
    
    # Test simple filename lookup
    result = scraping_index.lookup(Path('src'), Path('main.py'))
    assert result == Path('src/main.py')
    
    # Test disambiguation by proximity
    result = scraping_index.lookup(Path('test'), Path('main.py'))
    assert result == Path('test/main.py')
