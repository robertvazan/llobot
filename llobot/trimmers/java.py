from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.java import suffix

@cache
def package() -> Trimmer:
    return llobot.trimmers.re(r'^package [\w\.]+;\n+', re.MULTILINE) & suffix()

@cache
def imports() -> Trimmer:
    return llobot.trimmers.re(r'^import (?:static )?[\w\.\*]+;\n+', re.MULTILINE) & suffix()

@cache
def boilerplate() -> Trimmer:
    return package() + imports()

__all__ = [
    'package',
    'imports',
    'boilerplate'
]

