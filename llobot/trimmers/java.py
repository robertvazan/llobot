from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.java import suffix

@cache
def normalize_whitespace() -> Trimmer:
    return llobot.trimmers.normalize_whitespace() & suffix()

# This will strip multi-line comments from within multi-line string literals, but that's probably okay.
# This will also remove javadoc. We don't treat javadoc specially.
@cache
def block_comments() -> Trimmer:
    return llobot.trimmers.re(r'^ */\*.*?\*/\n', re.MULTILINE | re.DOTALL, incremental=incremental) & suffix()

# This will only work correctly if multi-line block comments are trimmed first.
# We don't care too much about surrounding whitespace. It is removed from the right side, which is more likely to work well.
@cache
def inline_comments() -> Trimmer:
    return llobot.trimmers.re(r'/\*.*?\*/ *') & suffix()

# This has the same issue with multi-line strings as above. This pattern will never match inside single-line strings.
@cache
def line_comments() -> Trimmer:
    return llobot.trimmers.re(r'^ *//.*\n', re.MULTILINE) & suffix()

# Trailing comments are tricky, because '//' can appear in strings.
# We guard against that case by excluding quotes '"' from comment content.
# That might result in some false negatives, but we don't care, because trimmers don't have to be perfect to do their job.
@cache
def trailing_comments() -> Trimmer:
    return llobot.trimmers.re(r' *//[^"\n]*$', re.MULTILINE) & suffix()

@cache
def comments() -> Trimmer:
    return block_comments() + inline_comments() + line_comments() + trailing_comments()

@cache
def package() -> Trimmer:
    return llobot.trimmers.re(r'^package [\w\.]+;\n+', re.MULTILINE) & suffix()

@cache
def imports() -> Trimmer:
    return llobot.trimmers.re(r'^import (?:static )?[\w\.\*]+;\n+', re.MULTILINE) & suffix()

@cache
def member_body(incremental=True) -> Trimmer:
    oneliner = llobot.trimmers.re(r'\{[^\n}]+\}$', re.MULTILINE, replacement=r'{}', incremental=incremental)
    multiline = llobot.trimmers.re(r'\{\n(?: {8}.*\n|\n)* {4}\}$', re.MULTILINE, replacement=r'{}', incremental=incremental)
    return (oneliner | multiline) & suffix()

@cache
def class_body() -> Trimmer:
    return llobot.trimmers.re(r'{.*}', re.DOTALL, replacement=r'{}') & suffix()

@cache
def tail() -> Trimmer:
    return llobot.trimmers.tail() & suffix()

@cache
def incremental() -> Trimmer:
    return comments() + member_body() + class_body() + tail()

@cache
def eager() -> Trimmer:
    return normalize_whitespace() + package() + imports()

__all__ = [
    'normalize_whitespace',
    'block_comments',
    'inline_comments',
    'line_comments',
    'trailing_comments',
    'comments',
    'package',
    'imports',
    'member_body',
    'class_body',
    'tail',
    'incremental',
    'eager'
]

