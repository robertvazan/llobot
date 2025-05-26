from functools import cache
from llobot.formatters.decorators import Decorator
import llobot.formatters.paths
import llobot.formatters.decorators
from llobot.knowledge.subsets.txt import suffix

@cache
def comment() -> Decorator:
    return llobot.formatters.decorators.path('# {}\n') & suffix()

@cache
def plain() -> Decorator:
    return llobot.formatters.decorators.path('{}\n\n') & suffix()

@cache
def bracketed() -> Decorator:
    return llobot.formatters.decorators.path('[ {} ]\n') & suffix()

@cache
def delimiter() -> Decorator:
    return llobot.formatters.decorators.path('----- {} -----\n') & suffix()

@cache
def underlined() -> Decorator:
    paths = llobot.formatters.paths.comment()
    def decorate(path: Path, content: str, note: str):
        formatted = paths(path, note)
        underline = '=' * len(formatted)
        return f"{formatted}\n{underline}\n\n{content}"
    return llobot.formatters.decorators.create(decorate) & suffix()

@cache
def standard() -> Decorator:
    return comment()

__all__ = [
    'comment',
    'plain',
    'bracketed',
    'delimiter',
    'underlined',
    'standard',
]

