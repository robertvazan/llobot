from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.scrapers import Scraper
import llobot.scrapers
import llobot.links.python
from llobot.knowledge.subsets.python import suffix

@cache
def simple_imports() -> Scraper:
    pattern = re.compile(r'^ *import ([\w_]+(?:\.[\w_]+)*)', re.MULTILINE)
    def scrape(content: str) -> Iterable[Link]:
        for module in pattern.findall(content):
            yield llobot.links.python.from_import(module)
    return llobot.scrapers.content(scrape) & suffix()

@cache
def from_imports() -> Scraper:
    pattern = re.compile(r'^ *from ([\w_]+(?:\.[\w_]+)*) import', re.MULTILINE)
    def scrape(path: Path, content: str) -> Iterable[Link]:
        for module in pattern.findall(content):
            yield llobot.links.python.from_from(module, path=path)
    return llobot.scrapers.create(scrape) & suffix()

@cache
def item_imports() -> Scraper:
    from_re = re.compile(r'^ *from ([\w_.]+) import ([\w_.]+(?: as [\w_]+)?(?:, [\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    multiline_re = re.compile(r'^ *from ([\w_.]+) import +\(\s*([\w_.]+(?: as [\w_]+)?(?:,\s*[\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    item_re = re.compile(r'([\w_.]+)(?: as [\w_]+)?')
    def scrape(path: Path, content: str) -> Iterable[Link]:
        for module, items in from_re.findall(content) + multiline_re.findall(content):
            for item in item_re.findall(items):
                yield llobot.links.python.from_import_item(module, item, path=path)
    return llobot.scrapers.create(scrape) & suffix()

@cache
def imports() -> Scraper:
    return simple_imports() | from_imports() | item_imports()

@cache
def standard() -> Scraper:
    return imports()

__all__ = [
    'simple_imports',
    'from_imports',
    'item_imports',
    'imports',
    'standard',
]

