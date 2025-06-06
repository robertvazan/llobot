from __future__ import annotations
from functools import cache, lru_cache, cached_property
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
import re

class EnvelopeFormatter:
    # May return None to indicate it cannot handle the file, which is useful for combining several formatters.
    def format(self, path: Path, content: str, note: str = '') -> str | None:
        return None

    def __call__(self, path: Path, content: str, note: str = '') -> str | None:
        return self.format(path, content, note)

    @cached_property
    def regex(self) -> re.Pattern | None:
        return None

    # Path can be None even if parsing succeeds, because some envelopes do not encode path.
    # Success is therefore signaled with non-empty content.
    def parse(self, formatted: str) -> tuple[Path | None, str]:
        return None, ''

    def parse_all(self, message: str) -> list[tuple[Path, str]]:
        if not self.regex:
            return []
        results = []
        for match in self.regex.finditer(message):
            path, content = self.parse(match.group(0))
            if path and content:
                results.append((path, content))
        return results

    def __or__(self, other: EnvelopeFormatter) -> EnvelopeFormatter:
        def parse(formatted: str) -> tuple[Path | None, str]:
            path, content = self.parse(formatted)
            if content:
                return path, content
            return other.parse(formatted)
        patterns = [f'(?:{regex.pattern})' for regex in (self.regex, other.regex) if regex]
        return create(
            lambda path, content, note: self(path, content, note) or other(path, content, note),
            lambda formatted: self.parse(formatted) if self.parse(formatted)[1] else other.parse(formatted),
            re.compile('|'.join(patterns), re.MULTILINE | re.DOTALL) if patterns else None
        )

    def __and__(self, whitelist: KnowledgeSubset | str) -> EnvelopeFormatter:
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        def parse(formatted: str) -> tuple[Path | None, str]:
            path, content = self.parse(formatted)
            if path and not whitelist(path, content):
                return None, ''
            return path, content
        return create(
            lambda path, content, note: self(path, content, note) if whitelist(path, content) else None,
            parse,
            self.regex
        )

def create(
    formatter: Callable[[Path, str, str], str | None],
    parser: Callable[[str], tuple[Path | None, str]] = lambda _: (None, ''),
    regex: re.Pattern | None = None
) -> EnvelopeFormatter:
    class LambdaEnvelopeFormatter(EnvelopeFormatter):
        def format(self, path: Path, content: str, note: str = '') -> str | None:
            return formatter(path, content, note)
        @cached_property
        def regex(self) -> re.Pattern | None:
            return regex
        def parse(self, formatted: str) -> tuple[Path | None, str]:
            return parser(formatted)
    return LambdaEnvelopeFormatter()

@cache
def vanilla() -> EnvelopeFormatter:
    return create(
        lambda path, content, note: content,
        lambda formatted: (None, formatted),
        re.compile(r'.+', re.MULTILINE | re.DOTALL)
    )

@lru_cache
def block(*,
    guesser: LanguageGuesser = llobot.formatters.languages.standard(),
    min_backticks: int = 3
) -> EnvelopeFormatter:
    def format(path: Path, content: str, note: str = '') -> str:
        lang = guesser(path, content)
        backtick_count = min_backticks
        backticks = '`' * backtick_count
        lines = content.splitlines()
        while any(line.startswith(backticks) for line in lines):
            backtick_count += 1
            backticks = '`' * backtick_count
        return f'{backticks}{lang}\n{content.strip()}\n{backticks}'
    detection_regex = re.compile(r'^(?:```[^`\n]*\n.*?\n```|````[^`\n]*\n.*?\n````|`````[^`\n]*\n.*?\n`````)$', re.MULTILINE | re.DOTALL)
    parsing_regex = re.compile(r'```+[^\n]*\n(.*)\n```+', re.MULTILINE | re.DOTALL)
    def parse(formatted: str) -> tuple[Path | None, str]:
        if not detection_regex.fullmatch(formatted):
            return None, ''
        match = parsing_regex.fullmatch(formatted)
        if not match:
            return None, ''
        return None, match.group(1)
    return create(format, parse, detection_regex)

@cache
def standard_body() -> EnvelopeFormatter:
    return block(min_backticks=4) & llobot.knowledge.subsets.markdown.suffix() | block()

# Best for unquoted content like Markdown.
@lru_cache
def details(paths: PathFormatter = llobot.formatters.paths.comment(), body: EnvelopeFormatter = vanilla()) -> EnvelopeFormatter:
    parseable = paths.regex and body.regex
    if parseable:
        detection_regex = re.compile(rf'^<details>\n<summary>{paths.regex.pattern}</summary>\n\n{body.regex.pattern}\n\n</details>$', re.MULTILINE | re.DOTALL)
        parsing_regex = re.compile(rf'<details>\n<summary>({paths.regex.pattern})</summary>\n\n({body.regex.pattern})\n\n</details>', re.MULTILINE | re.DOTALL)
    def parse(formatted: str) -> tuple[Path | None, str]:
        if not parseable or not detection_regex.fullmatch(formatted):
            return None, ''
        match = parsing_regex.fullmatch(formatted)
        if not match:
            return None, ''
        path = paths.parse(match.group(1))
        _, content = body.parse(match.group(2))
        if not path or not content:
            return None, ''
        return Path(path), content
    return create(
        lambda path, content, note: f'<details>\n<summary>{paths(path, note)}</summary>\n\n{body(path, content, note)}\n\n</details>',
        parse,
        detection_regex if parseable else None
    )

@lru_cache
def decorated(decorator: Decorator = llobot.formatters.decorators.minimal(), body: EnvelopeFormatter = standard_body()) -> EnvelopeFormatter:
    # Decorators don't currently support parsing.
    return create(lambda path, content, note: body(path, content, decorator(path, content, note)))

@lru_cache
def header(paths: PathFormatter = llobot.formatters.paths.standard(), body: EnvelopeFormatter = standard_body()) -> EnvelopeFormatter:
    parseable = paths.regex and body.regex
    if parseable:
        detection_regex = re.compile(f'^(?:{paths.regex.pattern})(?:{body.regex.pattern})$', re.MULTILINE | re.DOTALL)
        parsing_regex = re.compile(f'({paths.regex.pattern})({body.regex.pattern})', re.MULTILINE | re.DOTALL)
    def parse(formatted: str) -> tuple[Path | None, str]:
        if not parseable:
            return None, ''
        match = parsing_regex.fullmatch(formatted)
        if not match:
            return None, ''
        path = paths.parse(match.group(1))
        _, content = body.parse(match.group(2))
        if not path or not content:
            return None, ''
        return Path(path), content
    return create(
        lambda path, content, note: paths(path, note) + body(path, content, note),
        parse,
        detection_regex if parseable else None
    )

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

