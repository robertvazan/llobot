from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.markdown import suffix

@cache
def normalize_whitespace() -> Trimmer:
    return llobot.trimmers.normalize_whitespace() & suffix()

@cache
def tail() -> Trimmer:
    return llobot.trimmers.tail() & suffix()

@cache
def incremental() -> Trimmer:
    return tail()

@cache
def eager() -> Trimmer:
    return normalize_whitespace()

__all__ = [
    'normalize_whitespace',
    'tail',
    'incremental',
    'eager'
]

