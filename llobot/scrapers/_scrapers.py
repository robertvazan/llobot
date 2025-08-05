from __future__ import annotations
from functools import cache
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.links import Link
import llobot.knowledge.subsets

class Scraper:
    # Path may be a fallback '_.md' when scraping message content or other unnamed content.
    def scrape(self, path: Path, content: str) -> set[Link]:
        return set()

    def __call__(self, path: Path, content: str) -> set[Link]:
        return self.scrape(path, content)

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> Scraper:
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        return create(lambda path, content: self(path, content) if path in whitelist else set())

    def __or__(self, other: Scraper) -> Scraper:
        return create(lambda path, content: self(path, content) | other(path, content))

@cache
def none() -> Scraper:
    return Scraper()

def create(scrape: Callable[[Path, str], Iterable[Link]]) -> Scraper:
    class LambdaScraper(Scraper):
        def scrape(self, path: Path, content: str) -> set[Link]:
            return set(scrape(path, content))
    return LambdaScraper()

def path(scrape: Callable[[Path], Iterable[Link]]) -> Scraper:
    return create(lambda path, content: scrape(path))

def content(scrape: Callable[[str], Iterable[Link]]) -> Scraper:
    return create(lambda path, content: scrape(content))

@cache
def standard() -> Scraper:
    from llobot.scrapers import python, java, rust
    return (
        python.standard()
        | java.standard()
        | rust.standard())

__all__ = [
    'Scraper',
    'none',
    'create',
    'path',
    'content',
    'standard',
]
