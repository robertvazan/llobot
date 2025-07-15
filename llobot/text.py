from __future__ import annotations
import re

def terminate(text: str) -> str:
    """Adds a terminal newline to the text if it doesn't have one."""
    return text if not text or text.endswith('\n') else text + '\n'

def join(separator: str, documents: Iterable[str]) -> str:
    documents = [terminate(x) for x in documents if x and x.strip()]
    return separator.join(documents)

def concat(*documents: str) -> str:
    return join('\n', documents)

_DASHED_NAME_RE = re.compile('[^a-zA-Z0-9_]+')

def dashed_name(name) -> str:
    return _DASHED_NAME_RE.sub(' ', name).strip().replace(' ', '-')

# Language can be an empty string. Code block without language will be produced in that case.
def quote(lang: str, document: str, *, backtick_count: int = 3) -> str:
    while '`' * backtick_count in document:
        backtick_count += 1
    backticks = '`' * backtick_count
    return f'{backticks}{lang}\n{terminate(document)}{backticks}'

__all__ = [
    'terminate',
    'join',
    'concat',
    'dashed_name',
    'quote',
]
