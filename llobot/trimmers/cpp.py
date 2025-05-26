from functools import cache
import re
from llobot.trimmers import Trimmer
import llobot.trimmers
from llobot.knowledge.subsets.cpp import suffix

@cache
def normalize_whitespace() -> Trimmer:
    return llobot.trimmers.normalize_whitespace() & suffix()

@cache
def block_comments(incremental: bool = True) -> Trimmer:
    return llobot.trimmers.re(r'^ */\*.*?\*/\n', re.MULTILINE | re.DOTALL, incremental=incremental) & suffix()

# This will only work correctly if multi-line block comments are trimmed first.
# We don't care too much about surrounding whitespace. It is removed from the right side, which is more likely to work well.
@cache
def inline_comments() -> Trimmer:
    return llobot.trimmers.re(r'/\*.*?\*/ *') & suffix()

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
def includes() -> Trimmer:
    return llobot.trimmers.re(r'^#include.*\n', re.MULTILINE) & suffix()

@cache
def tail() -> Trimmer:
    return llobot.trimmers.tail() & suffix()

@cache
def incremental() -> Trimmer:
    return comments() + includes() + tail()

@cache
def eager() -> Trimmer:
    return normalize_whitespace()

__all__ = [
    'normalize_whitespace',
    'block_comments',
    'inline_comments',
    'line_comments',
    'trailing_comments',
    'comments',
    'tail',
    'incremental',
    'eager',
]

