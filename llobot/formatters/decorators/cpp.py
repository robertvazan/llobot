from functools import cache
from llobot.formatters.decorators import Decorator
import llobot.formatters.decorators
from llobot.knowledge.subsets.cpp import suffix

@cache
def path() -> Decorator:
    return llobot.formatters.decorators.path('// {}\n') & suffix()

__all__ = [
    'path',
]

