from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.xml import suffix

@cache
def normalize_whitespace() -> Trimmer:
    return llobot.trimmers.normalize_whitespace() & suffix()

@cache
def boilerplate() -> Trimmer:
    return normalize_whitespace()

__all__ = [
    'normalize_whitespace',
    'boilerplate'
]

