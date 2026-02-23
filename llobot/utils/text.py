"""Text manipulation utilities."""
from __future__ import annotations
import re
from typing import Iterable

# Matches C0 controls (excluding \t and \n), DEL, and C1 controls.
_CONTROL_CHAR_RE = re.compile(r'[\x00-\x08\x0b-\x1f\x7f\x80-\x9f]')

def sanitize_text(text: str) -> str:
    """
    Sanitizes text by escaping control characters.

    Preserves newlines (\\n) and tabs (\\t). Other control characters
    (C0 and C1 control sets + DEL) are replaced with their Python string literal
    representation (e.g., \\x1b for ESC).

    Args:
        text: The input text.

    Returns:
        Sanitized text.
    """
    def replace(match):
        return match.group().encode('unicode_escape').decode('ascii')

    return _CONTROL_CHAR_RE.sub(replace, text)

def terminate_document(text: str) -> str:
    """
    Adds a terminal newline to the text if it doesn't have one.

    Args:
        text: The input string.

    Returns:
        The text with a terminal newline.
    """
    return text if not text or text.endswith('\n') else text + '\n'

def normalize_document(document: str) -> str:
    """
    Normalizes a document by canonicalizing whitespace.

    Normalization consists of:
    - Removing trailing whitespace on all lines.
    - Removing empty lines at the beginning and end.
    - Ensuring the document is newline-terminated.

    Args:
        document: The document string to normalize.

    Returns:
        The normalized document.
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

def join_documents(separator: str, documents: Iterable[str | None]) -> str:
    """
    Joins a collection of documents with a separator.

    It ensures that all documents except the last one end with a newline before joining.
    The last document is not modified. This means the result is not terminated with a
    newline unless the last document was. Empty or whitespace-only documents are ignored.

    Args:
        separator: The separator to place between documents.
        documents: An iterable of document strings to join.

    Returns:
        A single string with the documents joined.
    """
    docs = [doc for doc in documents if doc and doc.strip()]
    if not docs:
        return ""
    if len(docs) == 1:
        return docs[0]
    terminated_front = [terminate_document(d) for d in docs[:-1]]
    return separator.join(terminated_front + [docs[-1]])

def concat_documents(*documents: str | None) -> str:
    """
    Concatenates several documents into a single one, separated by double newlines.

    This is suitable for creating a single text from multiple sections.
    The resulting string is not terminated with a newline unless the last document was.

    Args:
        *documents: A sequence of document strings to concatenate.

    Returns:
        The concatenated document.
    """
    return join_documents('\n', documents)

_DASHED_NAME_RE = re.compile('[^a-zA-Z0-9_]+')

def dashed_name(name: str) -> str:
    """
    Converts a string to a dashed name (kebab-case).

    Non-alphanumeric characters are replaced with spaces, which are then
    collapsed and replaced with dashes.

    Args:
        name: The string to convert.

    Returns:
        The dashed name.
    """
    return _DASHED_NAME_RE.sub(' ', name).strip().replace(' ', '-')

def truncate_lines(text: str, limit: int) -> str:
    """
    Truncates text to a maximum number of lines, removing lines from the middle.

    If the number of lines exceeds the limit, lines are removed from the middle
    of the text, and a message indicating the number of skipped lines is inserted.
    The first half of the limit (rounded down) is kept from the beginning, and
    the rest is kept from the end.

    Args:
        text: The input text.
        limit: The maximum number of lines.

    Returns:
        The truncated text with a notice about skipped lines.
    """
    lines = text.splitlines(keepends=True)
    if len(lines) <= limit:
        return text

    head_limit = limit // 2
    tail_limit = limit - head_limit

    head = lines[:head_limit]
    tail = lines[-tail_limit:] if tail_limit > 0 else []

    skipped = len(lines) - len(head) - len(tail)

    marker = f"... skipped {skipped} lines for brevity ...\n"

    return "".join(head) + marker + "".join(tail)

# Language can be an empty string. Code block without language will be produced in that case.
def markdown_code_block(lang: str, document: str, *, backtick_count: int = 3) -> str:
    """
    Formats a string as a Markdown code block.

    It automatically escapes backticks in the content by using a larger
    number of backticks for the fence.

    Args:
        lang: The language for syntax highlighting.
        document: The code or text to be placed in the block.
        backtick_count: The minimum number of backticks to use for the fence.

    Returns:
        A string containing the Markdown code block.
    """
    while '\n' + '`' * backtick_count in document or document.startswith('`' * backtick_count):
        backtick_count += 1
    backticks = '`' * backtick_count
    return f'{backticks}{lang}\n{terminate_document(document)}{backticks}'

def markdown_code_details(summary: str, lang: str, document: str, *, header: str = "", backtick_count: int = 3) -> str:
    """
    Wraps a document in HTML details/summary tags with a code block inside.

    The document is quoted using the specified language and then wrapped in
    details/summary tags for collapsible display.

    Args:
        summary: The text to display for the summary tag.
        lang: The language for syntax highlighting in the code block.
        document: The content to be placed in the code block.
        header: Optional text to display inside the details block before the code block.
        backtick_count: The minimum number of backticks for the code block fence.

    Returns:
        An HTML string with the details/summary and code block.
    """
    quoted = markdown_code_block(lang, document, backtick_count=backtick_count)
    header_part = f"{header}\n\n" if header else ""
    return f'<details>\n<summary>{summary}</summary>\n\n{header_part}{quoted}\n\n</details>'

def quote_code(text: str) -> str:
    """
    Quotes text as an inline Markdown code span.

    Surrounds text with backticks, ensuring that the fence is longer than any
    sequence of backticks in the text. Adds padding spaces if necessary (i.e.
    if the text begins or ends with a backtick).
    """
    if not text:
        return '``'

    max_backticks = 0
    current_backticks = 0
    for char in text:
        if char == '`':
            current_backticks += 1
        else:
            max_backticks = max(max_backticks, current_backticks)
            current_backticks = 0
    max_backticks = max(max_backticks, current_backticks)

    fence_length = max_backticks + 1
    fence = '`' * fence_length

    if text.startswith('`') or text.endswith('`'):
        return f'{fence} {text} {fence}'
    return f'{fence}{text}{fence}'

__all__ = [
    'sanitize_text',
    'terminate_document',
    'normalize_document',
    'join_documents',
    'concat_documents',
    'dashed_name',
    'truncate_lines',
    'markdown_code_block',
    'markdown_code_details',
    'quote_code',
]
