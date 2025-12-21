from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.overview import OverviewCrawler
from llobot.knowledge.subsets import coerce_subset

def test_overview_crawler():
    knowledge = Knowledge({
        PurePosixPath('README.md'): '',
        PurePosixPath('src/main.py'): '',
        PurePosixPath('src/utils/__init__.py'): '',
        PurePosixPath('src/utils/helpers.py'): '',
        PurePosixPath('docs/index.md'): '',
        PurePosixPath('docs/topics/feature.md'): '',
    })
    # Use standard overview subset
    crawler = OverviewCrawler()
    graph = crawler.crawl(knowledge)

    assert list(graph[PurePosixPath('src/main.py')].sorted()) == [PurePosixPath('README.md')]
    assert list(graph[PurePosixPath('src/utils/helpers.py')].sorted()) == [PurePosixPath('src/utils/__init__.py')]
    # 'docs/index.md' is not a standard overview, so feature.md links to root README.md
    assert list(graph[PurePosixPath('docs/topics/feature.md')].sorted()) == [PurePosixPath('README.md')]

def test_overview_crawler_custom_subset():
    knowledge = Knowledge({
        PurePosixPath('overview.txt'): '',
        PurePosixPath('module/file.py'): '',
    })
    # Custom subset for overview files
    subset = coerce_subset('*.txt')
    crawler = OverviewCrawler(subset=subset)
    graph = crawler.crawl(knowledge)
    assert list(graph[PurePosixPath('module/file.py')].sorted()) == [PurePosixPath('overview.txt')]
