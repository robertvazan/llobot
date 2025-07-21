from __future__ import annotations
import re

def terminate(text: str) -> str:
    """Adds a terminal newline to the text if it doesn't have one."""
    return text if not text or text.endswith('\n') else text + '\n'

def normalize(document: str) -> str:
    """
    Normalizes a document by:
    - Removing trailing whitespace on all lines
    - Removing empty lines at the beginning and end
    - Ensuring the document is newline-terminated
    """
    # Remove trailing whitespace on all lines
    lines = [line.rstrip() for line in document.splitlines()]

    # Remove empty lines at the beginning
    while lines and not lines[0]:
        lines.pop(0)

    # Remove empty lines at the end
    while lines and not lines[-1]:
        lines.pop()

    # Join lines and ensure newline termination
    if not lines:
        return ""

    return '\n'.join(lines) + '\n'

def join(separator: str, documents: Iterable[str | None]) -> str:
    """
    Joins a collection of documents with a separator.

    It ensures that all documents except the last one end with a newline before joining.
    The last document is not modified. This means the result is not terminated with a
    newline unless the last document was.
    """
    docs = [doc for doc in documents if doc and doc.strip()]
    if not docs:
        return ""
    if len(docs) == 1:
        return docs[0]
    terminated_front = [terminate(d) for d in docs[:-1]]
    return separator.join(terminated_front + [docs[-1]])

def concat(*documents: str | None) -> str:
    """
    Concatenates several documents into a single one, separated by double newlines.

    This is suitable for creating a single text from multiple sections.
    The resulting string is not terminated with a newline unless the last document was.
    """
    return join('\n', documents)

_DASHED_NAME_RE = re.compile('[^a-zA-Z0-9_]+')

def dashed_name(name) -> str:
    return _DASHED_NAME_RE.sub(' ', name).strip().replace(' ', '-')

# Language can be an empty string. Code block without language will be produced in that case.
def quote(lang: str, document: str, *, backtick_count: int = 3) -> str:
    while '\n' + '`' * backtick_count in document or document.startswith('`' * backtick_count):
        backtick_count += 1
    backticks = '`' * backtick_count
    return f'{backticks}{lang}\n{terminate(document)}{backticks}'

__all__ = [
    'terminate',
    'normalize',
    'join',
    'concat',
    'dashed_name',
    'quote',
]
