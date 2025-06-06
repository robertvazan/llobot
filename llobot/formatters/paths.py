from __future__ import annotations
from pathlib import Path
from functools import cache, cached_property
import re

class PathFormatter:
    # Path may be an already formatted string, in which case it is not manipulated.
    def format(self, path: Path | str, note: str = '') -> str:
        return str(path)

    def __call__(self, path: Path | str, note: str = '') -> str:
        return self.format(path, note)

    # Since format() can accept an already formatted string, we can only return string here.
    # Parsing may fail, in which case we just return an empty string.
    def parse(self, formatted: str) -> str:
        return ''

    @property
    def consumes_note(self) -> bool:
        return True

    @cached_property
    def regex(self) -> re.Pattern:
        patterns = []
        for formatted in list(dict.fromkeys([self('PLACEHOLDER'), self('PLACEHOLDER', 'PLACEHOLDER')])):
            pattern = re.escape(formatted).replace('PLACEHOLDER', r'[^\n]+?')
            patterns.append(pattern)
        return re.compile('|'.join(f'(?:{p})' for p in patterns) if len(patterns) > 1 else patterns[0])

    def __or__(self, other: PathFormatter) -> PathFormatter:
        return create(
            lambda path, note: other(self(path, note), '' if self.consumes_note else note),
            lambda formatted: self.parse(other.parse(formatted))
        )

def create(formatter: Callable[[Path | str, str], str], parser: Callable[[str], str] = lambda _: '') -> PathFormatter:
    class LambdaFormatter(PathFormatter):
        def format(self, path: Path | str, note: str = '') -> str:
            return formatter(path, note)
        def parse(self, formatted: str) -> str:
            return parser(formatted)
        @property
        def consumes_note(self) -> bool:
            return True
    return LambdaFormatter()

def create_filter(formatter: Callable[[Path | str, str], str], parser: Callable[[str], str] = lambda _: '') -> PathFormatter:
    class FilterFormatter(PathFormatter):
        def format(self, path: Path | str, note: str = '') -> str:
            return formatter(path, note)
        def parse(self, formatted: str) -> str:
            return parser(formatted)
        @property
        def consumes_note(self) -> bool:
            return False
    return FilterFormatter()

@cache
def pattern(basic_pattern: str, note_pattern: str = '') -> PathFormatter:
    basic_regex = re.compile(re.escape(basic_pattern.format('PATH')).replace(r'PATH', r'([^\n]+?)'))
    if note_pattern:
        note_regex = re.compile(re.escape(note_pattern.format('PATH', 'NOTE')).replace(r'PATH', r'([^\n]+?)').replace(r'NOTE', r'[^\n]*?'))
    else:
        note_regex = None
    def parse(formatted: str) -> str:
        for regex in (note_regex, basic_regex):
            if regex:
                match = re.fullmatch(regex, formatted)
                if match:
                    return match.group(1)
        return ''
    if note_pattern:
        return create(lambda path, note: note_pattern.format(path, note) if note else basic_pattern.format(path), parse)
    else:
        return create_filter(lambda path, note: basic_pattern.format(path), parse)

@cache
def line(basic_pattern: str, note_pattern: str = '') -> PathFormatter:
    return pattern(basic_pattern + '\n', note_pattern + '\n' if note_pattern else '')

@cache
def parens() -> PathFormatter:
    return pattern('{}', '{} ({})')

@cache
def filename() -> PathFormatter:
    return create_filter(lambda path, note: path.name if isinstance(path, Path) else path)

@cache
def abbreviated() -> PathFormatter:
    return create_filter(lambda path, note: f'.../{path.name}' if isinstance(path, Path) and path.parent != path else str(path))

@cache
def backtick() -> PathFormatter:
    return pattern('`{}`')

@cache
def header() -> PathFormatter:
    return pattern('{}:\n\n')

# Default formatter to use in decorators.
@cache
def comment() -> PathFormatter:
    return parens()

@cache
def standard() -> PathFormatter:
    return backtick() | parens() | header()

__all__ = [
    'PathFormatter',
    'create',
    'create_filter',
    'pattern',
    'line',
    'parens',
    'filename',
    'abbreviated',
    'backtick',
    'header',
    'comment',
    'standard',
]

