from __future__ import annotations
from functools import cache, lru_cache, cached_property
from pathlib import Path
import re
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.formatters.languages import LanguageGuesser
import llobot.knowledge.subsets
import llobot.knowledge.subsets.markdown
import llobot.formatters.languages

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

@lru_cache
def header(*, guesser: LanguageGuesser = llobot.formatters.languages.standard(), min_backticks: int = 3) -> EnvelopeFormatter:
    def format(path: Path, content: str, note: str = '') -> str:
        note_suffix = f' ({note})' if note else ''
        lang = guesser(path, content)

        # Determine backtick count
        backtick_count = min_backticks
        backticks = '`' * backtick_count
        lines = content.splitlines()
        while any(line.startswith(backticks) for line in lines):
            backtick_count += 1
            backticks = '`' * backtick_count

        return f'`{path}`{note_suffix}:\n\n{backticks}{lang}\n{content.strip()}\n{backticks}'
    
    detection_regex = re.compile(r'^`[^\n]+?`(?: \([^\n]*?\))?:\n\n(?:```[^`\n]*\n.*?\n```|````[^`\n]*\n.*?\n````|`````[^`\n]*\n.*?\n`````)$', re.MULTILINE | re.DOTALL)
    parsing_regex = re.compile(r'`([^\n]+?)`(?: \([^\n]*?\))?:\n\n```+[^\n]*\n(.*)\n```+', re.MULTILINE | re.DOTALL)
    
    def parse(formatted: str) -> tuple[Path | None, str]:
        if not detection_regex.fullmatch(formatted):
            return None, ''
        match = parsing_regex.fullmatch(formatted)
        if not match:
            return None, ''
        return Path(match.group(1)), match.group(2)

    return create(format, parse, detection_regex)

@cache
def standard() -> EnvelopeFormatter:
    return header(min_backticks=4) & llobot.knowledge.subsets.markdown.suffix() | header()

__all__ = [
    'EnvelopeFormatter',
    'create',
    'header',
    'standard',
]

