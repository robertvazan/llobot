from functools import cache
from llobot.formatters.decorators import Decorator
import llobot.formatters.decorators
from llobot.knowledge.subsets.java import properties as suffix

@cache
def path() -> Decorator:
    return llobot.formatters.decorators.path('# {}\n') & suffix()

__all__ = [
    'path',
]

