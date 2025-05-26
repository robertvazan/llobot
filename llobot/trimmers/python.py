from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.python import suffix

@cache
def normalize_whitespace() -> Trimmer:
    return llobot.trimmers.normalize_whitespace() & suffix()

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
def line_comments() -> Trimmer:
    return llobot.trimmers.re(r'^ *#.*\n', re.MULTILINE) & suffix()

@cache
def trailing_comments() -> Trimmer:
    return llobot.trimmers.re(r''' *#[^"'\n]*$''', re.MULTILINE) & suffix()

@cache
def comments() -> Trimmer:
    return line_comments() + trailing_comments()

@cache
def function_body(incremental=True) -> Trimmer:
    return llobot.trimmers.re(r'(^def .+?:\n)(?:\n* {4}[^\n]*\n)*', re.MULTILINE | re.DOTALL, replacement=r'\1', incremental=incremental) & suffix()

# This will also match functions defined inside other functions since it only cares about indentation.
@cache
def method_body(incremental=True) -> Trimmer:
    return llobot.trimmers.re(r'(^ {4}def .+?:\n)(?:\n* {8}[^\n]*\n)*', re.MULTILINE | re.DOTALL, replacement=r'\1', incremental=incremental) & suffix()

@cache
def class_body(incremental=True) -> Trimmer:
    return llobot.trimmers.re(r'(^class .+?:\n)(?:\n* {4}[^\n]*\n)*', re.MULTILINE | re.DOTALL, replacement=r'\1', incremental=incremental) & suffix()

@cache
def tail() -> Trimmer:
    return llobot.trimmers.tail() & suffix()

@cache
def incremental() -> Trimmer:
    return comments() + exports() + imports() + (method_body() | function_body()) + class_body() + tail()

@cache
def eager() -> Trimmer:
    return normalize_whitespace() + shebang()

__all__ = [
    'normalize_whitespace',
    'shebang',
    'imports',
    'exports',
    'line_comments',
    'trailing_comments',
    'comments',
    'function_body',
    'method_body',
    'class_body',
    'tail',
    'incremental',
    'eager'
]

