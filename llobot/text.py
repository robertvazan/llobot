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

__all__ = [
    'join',
    'concatenate',
    'dashed_name',
]

