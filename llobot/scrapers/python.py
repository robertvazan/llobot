from __future__ import annotations
from functools import cache
from collections import defaultdict
import re
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.scrapers import GraphScraper
import llobot.scrapers
import llobot.links.python

@cache
def simple_imports() -> GraphScraper:
    pattern = re.compile(r'^ *import ([\w_]+(?:\.[\w_]+)*)', re.MULTILINE)
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        graph = defaultdict(set)
        indexes = {}
        for path, content in knowledge:
            if path.suffix != '.py':
                continue
            for module in pattern.findall(content):
                link = llobot.links.python.from_import(module)
                for target in link.resolve_indexed(knowledge, indexes):
                    if target != path:
                        graph[path].add(target)
        return KnowledgeGraph({path: KnowledgeIndex(targets) for path, targets in graph.items()})
    return llobot.scrapers.create(scrape)

@cache
def from_imports() -> GraphScraper:
    pattern = re.compile(r'^ *from ([\w_.]+) import', re.MULTILINE)
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        graph = defaultdict(set)
        indexes = {}
        for path, content in knowledge:
            if path.suffix != '.py':
                continue
            for module in pattern.findall(content):
                link = llobot.links.python.from_from(module, path=path)
                if link:
                    for target in link.resolve_indexed(knowledge, indexes):
                        if target != path:
                            graph[path].add(target)
        return KnowledgeGraph({path: KnowledgeIndex(targets) for path, targets in graph.items()})
    return llobot.scrapers.create(scrape)

@cache
def item_imports() -> GraphScraper:
    from_re = re.compile(r'^ *from ([\w_.]+) import ([\w_.]+(?: as [\w_]+)?(?:, [\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    multiline_re = re.compile(r'^ *from ([\w_.]+) import +\(\s*([\w_.]+(?: as [\w_]+)?(?:,\s*[\w_.]+(?: as [\w_]+)?)*)', re.MULTILINE)
    item_re = re.compile(r'([\w_.]+)(?: as [\w_]+)?')
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        graph = defaultdict(set)
        indexes = {}
        for path, content in knowledge:
            if path.suffix != '.py':
                continue
            for module, items in from_re.findall(content) + multiline_re.findall(content):
                for item in item_re.findall(items):
                    link = llobot.links.python.from_import_item(module, item, path=path)
                    for target in link.resolve_indexed(knowledge, indexes):
                        if target != path:
                            graph[path].add(target)
        return KnowledgeGraph({path: KnowledgeIndex(targets) for path, targets in graph.items()})
    return llobot.scrapers.create(scrape)

@cache
def imports() -> GraphScraper:
    return simple_imports() | from_imports() | item_imports()

@cache
def standard() -> GraphScraper:
    return imports()

__all__ = [
    'simple_imports',
    'from_imports',
    'item_imports',
    'imports',
    'standard',
]
