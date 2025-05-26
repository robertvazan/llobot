from __future__ import annotations
from functools import cache
import re
from pathlib import Path
from llobot.links import Link
from llobot.scrapers import Scraper
import llobot.scrapers
import llobot.links
from llobot.knowledge.subsets.markdown import suffix

@cache
def backtick_path() -> Scraper:
    pattern = re.compile(r'`(/?(?:[A-Za-z_][\w.-]+/)*[A-Za-z_][\w.-]+\.[a-z]+)`')
    def scrape(content: str) -> Iterable[Link]:
        for hit in pattern.findall(content):
            yield llobot.links.absolute(hit[1:]) if hit.startswith('/') else llobot.links.abbreviated(hit)
    return llobot.scrapers.content(scrape) & suffix()

@cache
def standard() -> Scraper:
    return backtick_path()

@cache
def retrieval() -> Scraper:
    return backtick_path()

__all__ = [
    'backtick_path',
    'standard',
    'retrieval',
]

