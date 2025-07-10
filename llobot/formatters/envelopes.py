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

    def find(self, message: str) -> list[str]:
        return []

    # Success is signaled with non-None path and non-empty content.
    def parse(self, formatted: str) -> tuple[Path | None, str]:
        return None, ''

    def parse_all(self, message: str) -> list[tuple[Path, str]]:
        results = []
        for match in self.find(message):
            path, content = self.parse(match)
            if path and content:
                results.append((path, content))
        return results

    def __or__(self, other: EnvelopeFormatter) -> EnvelopeFormatter:
        myself = self
        class OrEnvelopeFormatter(EnvelopeFormatter):
            def format(self, path: Path, content: str, note: str = '') -> str | None:
                return myself.format(path, content, note) or other.format(path, content, note)
            def find(self, message: str) -> list[str]:
                return myself.find(message) + other.find(message)
            def parse(self, formatted: str) -> tuple[Path | None, str]:
                path, content = myself.parse(formatted)
                if content:
                    return path, content
                return other.parse(formatted)
        return OrEnvelopeFormatter()

    def __and__(self, whitelist: KnowledgeSubset | str) -> EnvelopeFormatter:
        myself = self
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        class AndEnvelopeFormatter(EnvelopeFormatter):
            def format(self, path: Path, content: str, note: str = '') -> str | None:
                return myself.format(path, content, note) if whitelist(path, content) else None
            def find(self, message: str) -> list[str]:
                return myself.find(message)
            def parse(self, formatted: str) -> tuple[Path | None, str]:
                path, content = myself.parse(formatted)
                if path and not whitelist(path, content):
                    return None, ''
                return path, content
        return AndEnvelopeFormatter()

@lru_cache
def header(*,
    guesser: LanguageGuesser = llobot.formatters.languages.standard(),
    quad_backticks: list[str] = ['markdown'],
) -> EnvelopeFormatter:
    detection_regex = re.compile(r'^`[^\n]+?`(?: \([^\n]*?\))?:\n\n?(?:```[^`\n]*\n.*?\n```|````[^`\n]*\n.*?\n````|`````[^`\n]*\n.*?\n`````)$', re.MULTILINE | re.DOTALL)
    parsing_regex = re.compile(r'`([^\n]+?)`(?: \([^\n]*?\))?:\n\n?```+[^\n]*\n(.*)\n```+', re.MULTILINE | re.DOTALL)
    class HeaderEnvelopeFormatter(EnvelopeFormatter):
        def format(self, path: Path, content: str, note: str = '') -> str:
            note_suffix = f' ({note})' if note else ''
            lang = guesser(path, content)

            # Determine backtick count
            backtick_count = 4 if lang in quad_backticks else 3
            backticks = '`' * backtick_count
            lines = content.splitlines()
            while any(line.startswith(backticks) for line in lines):
                backtick_count += 1
                backticks = '`' * backtick_count

            return f'`{path}`{note_suffix}:\n\n{backticks}{lang}\n{content.strip()}\n{backticks}'

        def find(self, message: str) -> list[str]:
            return [match.group(0) for match in detection_regex.finditer(message)]

        def parse(self, formatted: str) -> tuple[Path | None, str]:
            if not detection_regex.fullmatch(formatted):
                return None, ''
            match = parsing_regex.fullmatch(formatted)
            if not match:
                return None, ''
            return Path(match.group(1)), match.group(2)
    return HeaderEnvelopeFormatter()

@cache
def standard() -> EnvelopeFormatter:
    return header()

__all__ = [
    'EnvelopeFormatter',
    'create',
    'header',
    'standard',
]

