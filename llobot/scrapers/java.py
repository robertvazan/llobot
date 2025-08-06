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
import llobot.links.java

@cache
def pascal_case() -> GraphScraper:
    comment_re = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)
    text_block_re = re.compile(r'"""(?:[^\\]|\\.)*?"""', re.DOTALL)
    string_re = re.compile(r'"(?:[^"\\]|\\.)*"')
    pattern = re.compile(r'\b[A-Z][A-Za-z0-9]*\b')
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        graph = defaultdict(set)
        indexes = {}
        for path, content in knowledge:
            if path.suffix != '.java':
                continue
            content = comment_re.sub(' ', content)
            content = text_block_re.sub(' ', content)
            content = string_re.sub(' ', content)
            for name in pattern.findall(content):
                # Require at least one lowercase letter to avoid matching enums and constants.
                if not name.isupper():
                    link = llobot.links.java.type_name(name)
                    for target in link.resolve_indexed(knowledge, indexes):
                        if target != path:
                            graph[path].add(target)
        return KnowledgeGraph({path: KnowledgeIndex(targets) for path, targets in graph.items()})
    return llobot.scrapers.create(scrape)

@cache
def standard() -> GraphScraper:
    return pascal_case()

__all__ = [
    'pascal_case',
    'standard',
]
