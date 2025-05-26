from functools import cache
from llobot.formatters.decorators import Decorator
import llobot.formatters.decorators
from llobot.knowledge.subsets.markdown import suffix

@cache
def details() -> Decorator:
    return llobot.formatters.decorators.details() & suffix()

__all__ = [
    'details',
]

