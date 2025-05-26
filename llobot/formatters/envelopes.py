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

# Language can be an empty string. Code block without language will be produced in that case.
def quote(lang: str, document: str) -> str:
    backtick_count = 3
    while '`' * backtick_count in document:
        backtick_count += 1
    backticks = '`' * backtick_count
    return f'{backticks}{lang}\n{document.strip()}\n{backticks}'

def quote_file(path: Path, content: str, guesser: LanguageGuesser | None = llobot.formatters.languages.standard()) -> str:
    return quote(guesser(path, content), content) if guesser else content.strip()

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

# Best for unquoted content like Markdown. If guesser is provided, content inside the details tag will be wrapped in a code block.
@lru_cache
def details(paths: PathFormatter = llobot.formatters.paths.comment(), guesser: LanguageGuesser | None = None) -> EnvelopeFormatter:
    return create(lambda path, content, note: f'<details>\n<summary>{paths(path, note)}</summary>\n\n{quote_file(path, content, guesser)}\n\n</details>')

@lru_cache
def decorated(decorator: Decorator = llobot.formatters.decorators.minimal(), guesser: LanguageGuesser | None = llobot.formatters.languages.standard()) -> EnvelopeFormatter:
    if guesser:
        return create(lambda path, content, note: quote(guesser(path, content), decorator(path, content, note)))
    else:
        return create(lambda path, content, note: decorator(path, content, note))

@lru_cache
def header(paths: PathFormatter = llobot.formatters.paths.standard(), guesser: LanguageGuesser | None = llobot.formatters.languages.standard()) -> EnvelopeFormatter:
    return create(lambda path, content, note: paths(path, note) + quote_file(path, content, guesser))

@cache
def standard() -> EnvelopeFormatter:
    return details() & llobot.knowledge.subsets.markdown.suffix() | decorated()

__all__ = [
    'quote',
    'quote_file',
    'EnvelopeFormatter',
    'create',
    'details',
    'decorated',
    'header',
    'standard',
]

