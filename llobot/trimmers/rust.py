from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.rust import suffix

@cache
def uses() -> Trimmer:
    return llobot.trimmers.re(r'^ *(?:pub )?use [^;]+;\n+', re.MULTILINE) & suffix()

@cache
def mod_declarations() -> Trimmer:
    return llobot.trimmers.re(r'^ *(?:pub )?mod ([\w_]+);\n+', re.MULTILINE) & suffix()

@cache
def boilerplate() -> Trimmer:
    return mod_declarations() + uses()

__all__ = [
    'uses',
    'mod_declarations',
    'boilerplate'
]

