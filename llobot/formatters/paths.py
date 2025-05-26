from __future__ import annotations
from pathlib import Path
from functools import cache

class PathFormatter:
    # Path may be an already formatted string, in which case it is not manipulated.
    def format(self, path: Path | str, note: str = '') -> str:
        return str(path)

    def __call__(self, path: Path | str, note: str = '') -> str:
        return self.format(path, note)

    def consumes_note(self) -> bool:
        return True

    def __or__(self, other: PathFormatter) -> PathFormatter:
        return create(lambda path, note: other(self(path, note), '' if self.consumes_note() else note))

def create(function: Callable[[Path | str, str], str]) -> PathFormatter:
    class LambdaFormatter(PathFormatter):
        def format(self, path: Path | str, note: str = '') -> str:
            return function(path, note)
        def consumes_note(self) -> bool:
            return True
    return LambdaFormatter()

def create_filter(function: Callable[[Path | str, str], bool]) -> PathFilter:
    class FilterFormatter(PathFormatter):
        def format(self, path: Path | str, note: str = '') -> str:
            return function(path, note)
        def consumes_note(self) -> bool:
            return False
    return FilterFormatter()

@cache
def pattern(basic_pattern: str, note_pattern: str = '') -> PathFormatter:
    if note_pattern:
        return create(lambda path, note: note_pattern.format(path, note) if note else basic_pattern.format(path))
    else:
        return create_filter(lambda path, note: basic_pattern.format(path))

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

