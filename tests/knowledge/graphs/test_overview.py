from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.overview import OverviewCrawler
from llobot.knowledge.subsets import coerce_subset

def test_overview_crawler():
    knowledge = Knowledge({
        Path('README.md'): '',
        Path('src/main.py'): '',
        Path('src/utils/__init__.py'): '',
        Path('src/utils/helpers.py'): '',
        Path('docs/index.md'): '',
        Path('docs/topics/feature.md'): '',
    })
    # Use standard overview subset
    crawler = OverviewCrawler()
    graph = crawler.crawl(knowledge)

    assert list(graph[Path('src/main.py')].sorted()) == [Path('README.md')]
    assert list(graph[Path('src/utils/helpers.py')].sorted()) == [Path('src/utils/__init__.py')]
    # 'docs/index.md' is not a standard overview, so feature.md links to root README.md
    assert list(graph[Path('docs/topics/feature.md')].sorted()) == [Path('README.md')]

def test_overview_crawler_custom_subset():
    knowledge = Knowledge({
        Path('overview.txt'): '',
        Path('module/file.py'): '',
    })
    # Custom subset for overview files
    subset = coerce_subset('*.txt')
    crawler = OverviewCrawler(subset=subset)
    graph = crawler.crawl(knowledge)
    assert list(graph[Path('module/file.py')].sorted()) == [Path('overview.txt')]
