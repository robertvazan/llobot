from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.python import (
    PythonSimpleImportsCrawler,
    PythonFromImportsCrawler,
    PythonItemImportsCrawler,
)

KNOWLEDGE = Knowledge({
    Path('main.py'): "import utils.helpers\nfrom services import api",
    Path('utils/helpers.py'): "from . import constants",
    Path('utils/constants.py'): "",
    Path('services/__init__.py'): "from .api import ApiService",
    Path('services/api.py'): "",
    Path('vendor/pkg/sub.py'): "",
    Path('importer.py'): "import vendor.pkg.sub",
})

def test_python_simple_imports_crawler():
    crawler = PythonSimpleImportsCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[Path('main.py')].sorted()) == [Path('utils/helpers.py')]
    assert list(graph[Path('importer.py')].sorted()) == [Path('vendor/pkg/sub.py')]

def test_python_from_imports_crawler():
    crawler = PythonFromImportsCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[Path('main.py')].sorted()) == [Path('services/__init__.py')]
    assert list(graph[Path('services/__init__.py')].sorted()) == [Path('services/api.py')]
    assert list(graph[Path('utils/helpers.py')].sorted()) == []

def test_python_item_imports_crawler():
    knowledge = Knowledge({
        Path('main.py'): "from utils import helpers",
        Path('utils/__init__.py'): "",
        Path('utils/helpers.py'): "",
    })
    crawler = PythonItemImportsCrawler()
    graph = crawler.crawl(knowledge)
    assert list(graph[Path('main.py')].sorted()) == [Path('utils/helpers.py')]

    graph2 = crawler.crawl(KNOWLEDGE)
    assert list(graph2[Path('utils/helpers.py')].sorted()) == [Path('utils/constants.py')]
