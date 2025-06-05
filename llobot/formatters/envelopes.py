from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets
import llobot.knowledge.subsets.markdown
import llobot.formatters.languages
import llobot.formatters.paths
import llobot.formatters.decorators
from llobot.formatters.languages import LanguageGuesser
from llobot.formatters.paths import PathFormatter
from llobot.formatters.decorators import Decorator

class EnvelopeFormatter:
    # May return None to indicate it cannot handle the file, which is useful for combining several formatters.
    def wrap(self, path: Path, content: str, note: str = '') -> str | None:
        return None

    def __call__(self, path: Path, content: str, note: str = '') -> str | None:
        return self.wrap(path, content, note)

    def __or__(self, other: EnvelopeFormatter) -> EnvelopeFormatter:
        return create(lambda path, content, note: self(path, content, note) or other(path, content, note))

    def __and__(self, whitelist: KnowledgeSubset | str) -> EnvelopeFormatter:
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        return create(lambda path, content, note: self(path, content, note) if whitelist(path, content) else None)

def create(function: Callable[[Path, str, str], str | None]) -> EnvelopeFormatter:
    class LambdaEnvelopeFormatter(EnvelopeFormatter):
        def wrap(self, path: Path, content: str, note: str = '') -> str | None:
            return function(path, content, note)
    return LambdaEnvelopeFormatter()

@cache
def vanilla() -> EnvelopeFormatter:
    return create(lambda path, content, note: content)

@lru_cache
def block(*,
    guesser: LanguageGuesser = llobot.formatters.languages.standard(),
    min_backticks: int = 3
) -> EnvelopeFormatter:
    def wrap(path: Path, content: str, note: str = '') -> str:
        lang = guesser(path, content)
        backtick_count = min_backticks
        while '`' * backtick_count in content:
            backtick_count += 1
        backticks = '`' * backtick_count
        return f'{backticks}{lang}\n{content.strip()}\n{backticks}'
    return create(wrap)

@cache
def standard_body() -> EnvelopeFormatter:
    return block()

# Best for unquoted content like Markdown.
@lru_cache
def details(paths: PathFormatter = llobot.formatters.paths.comment(), body: EnvelopeFormatter = vanilla()) -> EnvelopeFormatter:
    return create(lambda path, content, note: f'<details>\n<summary>{paths(path, note)}</summary>\n\n{body(path, content, note)}\n\n</details>')

@lru_cache
def decorated(decorator: Decorator = llobot.formatters.decorators.minimal(), body: EnvelopeFormatter = standard_body()) -> EnvelopeFormatter:
    return create(lambda path, content, note: body(path, content, decorator(path, content, note)))

@lru_cache
def header(paths: PathFormatter = llobot.formatters.paths.standard(), body: EnvelopeFormatter = standard_body()) -> EnvelopeFormatter:
    return create(lambda path, content, note: paths(path, note) + body(path, content, note))

@cache
def standard() -> EnvelopeFormatter:
    return header()

__all__ = [
    'EnvelopeFormatter',
    'create',
    'vanilla',
    'block',
    'standard_body',
    'details',
    'decorated',
    'header',
    'standard',
]

