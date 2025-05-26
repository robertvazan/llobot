from functools import cache
from llobot.formatters.decorators import Decorator
import llobot.formatters.decorators
import llobot.knowledge.subsets.java

@cache
def path() -> Decorator:
    return llobot.formatters.decorators.path('// {}\n') & llobot.knowledge.subsets.java.suffix()

@cache
def filename() -> Decorator:
    return llobot.formatters.decorators.filename('// {}\n') & llobot.knowledge.subsets.java.regular()

@cache
def abbreviated() -> Decorator:
    return llobot.formatters.decorators.abbreviated('// {}\n') & llobot.knowledge.subsets.java.regular()

@cache
def minimal() -> Decorator:
    return path() & llobot.knowledge.subsets.java.special()

__all__ = [
    'path',
    'filename',
    'abbreviated',
    'minimal',
]

