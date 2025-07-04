from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.python import suffix

@cache
def shebang() -> Trimmer:
    return llobot.trimmers.re(r'^#!.*\n+') & suffix()

@cache
def imports() -> Trimmer:
    return (
        llobot.trimmers.re(r'^import .*\n+', re.MULTILINE) +
        llobot.trimmers.re(r'^from [\w_\.]+ import [^(\n]*\n+', re.MULTILINE) +
        llobot.trimmers.re(r'^from [\w_\.]+ import +\([^)]*\)\n+', re.MULTILINE)
    ) & suffix()

@cache
def exports() -> Trimmer:
    return llobot.trimmers.re(r'''^__all__ = \[\s*['"][\w_]+['"](?:,\s*['"][\w_]+['"])*,?\s*\]\n+''', re.MULTILINE) & suffix()

@cache
def boilerplate() -> Trimmer:
    return shebang()

__all__ = [
    'shebang',
    'imports',
    'exports',
    'boilerplate'
]

