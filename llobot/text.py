from __future__ import annotations
import re

def join(separator: str, documents: Iterable[str]) -> str:
    documents = [x.strip() for x in documents if x.strip()]
    if not documents:
        return ''
    return separator.join([x + '\n' for x in documents]).strip()

def concat(*documents: str) -> str:
    return join('\n', documents)

_DASHED_NAME_RE = re.compile('[^a-zA-Z0-9]+')

def dashed_name(name) -> str:
    return _DASHED_NAME_RE.sub(' ', name).strip().replace(' ', '-')

# Language can be an empty string. Code block without language will be produced in that case.
def quote(lang: str, document: str, *, backtick_count: int = 3) -> str:
    while '`' * backtick_count in document:
        backtick_count += 1
    backticks = '`' * backtick_count
    return f'{backticks}{lang}\n{document.strip()}\n{backticks}'

__all__ = [
    'join',
    'concatenate',
    'dashed_name',
    'quote',
]

