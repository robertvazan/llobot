from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.scrapers import GraphScraper
import llobot.scrapers
import llobot.scrapers.index

@cache
def pascal_case() -> GraphScraper:
    comment_re = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)
    text_block_re = re.compile(r'"""(?:[^\\]|\\.)*?"""', re.DOTALL)
    string_re = re.compile(r'"(?:[^"\\]|\\.)*"')
    pattern = re.compile(r'\b[A-Z][A-Za-z0-9]*\b')
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        index = llobot.scrapers.index.create(knowledge)
        for path, content in knowledge:
            if path.suffix == '.java':
                content = comment_re.sub(' ', content)
                content = text_block_re.sub(' ', content)
                content = string_re.sub(' ', content)
                names = set(pattern.findall(content))
                for name in names:
                    # Require at least one lowercase letter to avoid matching enums and constants.
                    if not name.isupper():
                        target = index.lookup(path, Path(f'{name}.java'))
                        if target:
                            builder.add(path, target)
        return builder.build()
    return llobot.scrapers.create(scrape)

@cache
def standard() -> GraphScraper:
    return pascal_case()

__all__ = [
    'pascal_case',
    'standard',
]
