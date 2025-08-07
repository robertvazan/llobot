from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.scrapers import GraphScraper
import llobot.scrapers
import llobot.links.rust

@cache
def submodule() -> GraphScraper:
    pattern = re.compile(r'^ *(?:pub )?mod ([\w_]+);', re.MULTILINE)
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        indexes = {}
        for path, content in knowledge:
            if path.suffix == '.rs':
                for module in pattern.findall(content):
                    link = llobot.links.rust.submodule(path, module)
                    for target in link.resolve_indexed(knowledge, indexes):
                        builder.add(path, target)
        return builder.build()
    return llobot.scrapers.create(scrape)

@cache
def use() -> GraphScraper:
    statement_pattern = re.compile(r'^( *)(?:pub )?use ([^;]+);', re.MULTILINE)
    brace_pattern = re.compile(r'([\w_:]*){([^{}]*)}')
    item_pattern = re.compile(r'([\w_:]+)')
    def expand(matched) -> str:
        prefix = matched[1]
        return ', '.join([(prefix + item if prefix else item) for item in item_pattern.findall(matched[2])])
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        indexes = {}
        for path, content in knowledge:
            if path.suffix == '.rs':
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
                            for target in link.resolve_indexed(knowledge, indexes):
                                builder.add(path, target)
        return builder.build()
    return llobot.scrapers.create(scrape)

@cache
def standard() -> GraphScraper:
    # Including submodule references by default is a bit controversial,
    # because parent does not depend on the submodule just because it exists.
    # It is however common for dependency relationship to match submodule relationship.
    return submodule() | use()

__all__ = [
    'submodule',
    'use',
    'standard',
]
