from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph, KnowledgeGraphBuilder
from llobot.scrapers import GraphScraper, create_scraper
from llobot.scrapers.index import create_scraping_index

@cache
def pascal_case_java_scraper() -> GraphScraper:
    comment_re = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)
    text_block_re = re.compile(r'"""(?:[^\\]|\\.)*?"""', re.DOTALL)
    string_re = re.compile(r'"(?:[^"\\]|\\.)*"')
    pattern = re.compile(r'\b[A-Z][A-Za-z0-9]*\b')
    def scrape(knowledge: Knowledge) -> KnowledgeGraph:
        builder = KnowledgeGraphBuilder()
        index = create_scraping_index(knowledge)
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
    return create_scraper(scrape)

@cache
def standard_java_scraper() -> GraphScraper:
    return pascal_case_java_scraper()

__all__ = [
    'pascal_case_java_scraper',
    'standard_java_scraper',
]
