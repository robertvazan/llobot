from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.scrapers import Scraper
import llobot.scrapers
import llobot.links.rust
from llobot.knowledge.subsets.rust import suffix

@cache
def submodule() -> Scraper:
    pattern = re.compile(r'^ *(?:pub )?mod ([\w_]+);', re.MULTILINE)
    def scrape(path: Path, content: str) -> Iterable[Link]:
        for module in pattern.findall(content):
            yield llobot.links.rust.submodule(path, module)
    return llobot.scrapers.create(scrape) & suffix()

@cache
def use() -> Scraper:
    statement_pattern = re.compile(r'^( *)(?:pub )?use ([^;]+);', re.MULTILINE)
    brace_pattern = re.compile(r'([\w_:]*){([^{}]*)}')
    item_pattern = re.compile(r'([\w_:]+)')
    def expand(matched) -> str:
        prefix = matched[1]
        return ', '.join([(prefix + item if prefix else item) for item in item_pattern.findall(matched[2])])
    def scrape(path: Path, content: str) -> Iterable[Link]:
        for indentation, spec in statement_pattern.findall(content):
            while True:
                expanded = brace_pattern.sub(expand, spec)
                if expanded == spec:
                    break
                spec = expanded
            source = path
            while indentation:
                source = source/'nested-module'
                indentation = indentation[4:]
            for item in item_pattern.findall(spec):
                link = llobot.links.rust.use(source, item)
                if link:
                    yield link
    return llobot.scrapers.create(scrape) & suffix()

@cache
def standard() -> Scraper:
    # Including submodule references by default is a bit controversial,
    # because parent does not depend on the submodule just because it exists.
    # It is however common for dependency relationship to match submodule relationship.
    return submodule() | use()

__all__ = [
    'submodule',
    'use',
    'standard',
]

