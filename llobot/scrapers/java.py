from __future__ import annotations
from functools import cache
import re
from llobot.scrapers import Scraper
import llobot.scrapers
import llobot.links.java
from llobot.knowledge.subsets.java import suffix

@cache
def pascal_case() -> Scraper:
    comment_re = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)
    text_block_re = re.compile(r'"""(?:[^\\]|\\.)*?"""', re.DOTALL)
    string_re = re.compile(r'"(?:[^"\\]|\\.)*"')
    pattern = re.compile(r'\b[A-Z][A-Za-z0-9]*\b')
    def scrape(content: str) -> Iterable[Link]:
        content = comment_re.sub(' ', content)
        content = text_block_re.sub(' ', content)
        content = string_re.sub(' ', content)
        for name in pattern.findall(content):
            # Require at least one lowercase letter to avoid matching enums and constants.
            if not name.isupper():
                yield llobot.links.java.type_name(name)
    return llobot.scrapers.content(scrape) & suffix()

@cache
def standard() -> Scraper:
    return pascal_case()

__all__ = [
    'pascal_case',
    'standard',
]

