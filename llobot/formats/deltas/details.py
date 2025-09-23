"""
Document delta format using HTML details blocks.
"""
from __future__ import annotations
from pathlib import Path
import re
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.formats.deltas.documents import DocumentDeltaFormat
from llobot.formats.languages import LanguageMapping, standard_language_mapping
from llobot.utils.text import markdown_code_details, normalize_document
from llobot.utils.values import ValueTypeMixin

# Build regex for multi-backtick code blocks (3-10 backticks)
_CODE_BLOCK_PATTERN = '|'.join(rf'{"`" * i}[^`\n]*\n.*?^{"`" * i}' for i in range(3, 11))

# Regex for complete details block with file listing
_DETAILS_PATTERN = rf'<details>\n<summary>[^\n]+</summary>\n\n(?:{_CODE_BLOCK_PATTERN})\n\n</details>'

# Regex for one-line operations (must be on their own line)
_REMOVED_PATTERN = r'^Removed: `([^`]+)`$'
_MOVED_PATTERN = r'^Moved: `([^`]+)` => `([^`]+)`$'

# Combined detection regex: details blocks, bare code blocks (to skip), or one-line operations
_DETECTION_REGEX = re.compile(
    f'^(?:(?:{_DETAILS_PATTERN})|(?:{_CODE_BLOCK_PATTERN})|(?:{_REMOVED_PATTERN})|(?:{_MOVED_PATTERN}))$',
    re.MULTILINE | re.DOTALL
)

# Unified parsing regex for details blocks
_DETAILS_PARSING_RE = re.compile(rf'<details>\n<summary>File: ([^\n]+?)</summary>\n\n```+[^\n]*\n(.*)^```+\n\n</details>', re.MULTILINE | re.DOTALL)

# Parsing regexes for one-line operations
_REMOVED_RE = re.compile(_REMOVED_PATTERN, re.MULTILINE)
_MOVED_RE = re.compile(_MOVED_PATTERN, re.MULTILINE)


class DetailsDocumentDeltaFormat(DocumentDeltaFormat, ValueTypeMixin):
    """
    A document delta format using HTML details blocks and one-line operations.

    This format handles:
    - File listings: <details><summary>File: path</summary>```content```</details>
    - Removals: Removed: `path/to/file.py`
    - Moves: Moved: `old/path.py` => `new/path.py`
    """
    _languages: LanguageMapping
    _quad_backticks: tuple[str, ...]

    def __init__(self, *,
        languages: LanguageMapping = standard_language_mapping(),
        quad_backticks: tuple[str, ...] = ('markdown',),
    ):
        """
        Creates a new details document delta format.

        Args:
            languages: Language mapping for syntax highlighting.
            quad_backticks: Languages requiring 4+ backticks (e.g., when content has markdown).
        """
        self._languages = languages
        self._quad_backticks = quad_backticks

    def render(self, delta: DocumentDelta) -> str:
        # Handle removals
        if delta.removed:
            return f"Removed: `{delta.path}`"

        # Handle pure moves (no content)
        if delta.moved:
            return f"Moved: `{delta.moved_from}` => `{delta.path}`"

        # Handle file listings with content
        content = delta.content
        if content is None:
            return "" # Should not happen based on DocumentDelta validation
        summary = f'File: {delta.path}'
        lang = self._languages.resolve(delta.path)

        backtick_count = 4 if lang in self._quad_backticks else 3
        return markdown_code_details(summary, lang, content, backtick_count=backtick_count)

    def find(self, message: str) -> list[str]:
        return [match.group(0) for match in _DETECTION_REGEX.finditer(message)]

    def parse(self, formatted: str) -> DocumentDelta | None:
        formatted = formatted.strip()

        # Try parsing removal
        removed_match = _REMOVED_RE.fullmatch(formatted)
        if removed_match:
            path = Path(removed_match.group(1))
            return DocumentDelta(path, None, removed=True)

        # Try parsing move
        moved_match = _MOVED_RE.fullmatch(formatted)
        if moved_match:
            source_path = Path(moved_match.group(1))
            dest_path = Path(moved_match.group(2))
            return DocumentDelta(dest_path, None, moved_from=source_path)

        # Try parsing details block
        details_match = _DETAILS_PARSING_RE.fullmatch(formatted)
        if details_match:
            path_str, content = details_match.groups()
            path = Path(path_str.strip())
            content = normalize_document(content)
            return DocumentDelta(path, content)

        return None

__all__ = [
    'DetailsDocumentDeltaFormat',
]
