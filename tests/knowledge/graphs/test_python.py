from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.python import (
    PythonSimpleImportsCrawler,
    PythonFromImportsCrawler,
    PythonItemImportsCrawler,
)

KNOWLEDGE = Knowledge({
    PurePosixPath('main.py'): "import utils.helpers\nfrom services import api",
    PurePosixPath('utils/helpers.py'): "from . import constants",
    PurePosixPath('utils/constants.py'): "",
    PurePosixPath('services/__init__.py'): "from .api import ApiService",
    PurePosixPath('services/api.py'): "",
    PurePosixPath('vendor/pkg/sub.py'): "",
    PurePosixPath('importer.py'): "import vendor.pkg.sub",
})

def test_python_simple_imports_crawler():
    crawler = PythonSimpleImportsCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[PurePosixPath('main.py')].sorted()) == [PurePosixPath('utils/helpers.py')]
    assert list(graph[PurePosixPath('importer.py')].sorted()) == [PurePosixPath('vendor/pkg/sub.py')]

def test_python_from_imports_crawler():
    crawler = PythonFromImportsCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[PurePosixPath('main.py')].sorted()) == [PurePosixPath('services/__init__.py')]
    assert list(graph[PurePosixPath('services/__init__.py')].sorted()) == [PurePosixPath('services/api.py')]
    assert list(graph[PurePosixPath('utils/helpers.py')].sorted()) == []

def test_python_item_imports_crawler():
    knowledge = Knowledge({
        PurePosixPath('main.py'): "from utils import helpers",
        PurePosixPath('utils/__init__.py'): "",
        PurePosixPath('utils/helpers.py'): "",
    })
    crawler = PythonItemImportsCrawler()
    graph = crawler.crawl(knowledge)
    assert list(graph[PurePosixPath('main.py')].sorted()) == [PurePosixPath('utils/helpers.py')]

    graph2 = crawler.crawl(KNOWLEDGE)
    assert list(graph2[PurePosixPath('utils/helpers.py')].sorted()) == [PurePosixPath('utils/constants.py')]
