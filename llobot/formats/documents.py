"""
Document formats for knowledge deltas.

This module provides formats that can serialize DocumentDelta objects into
readable text formats and parse them back. The primary format uses HTML
details blocks for file listings and simple one-line formats for operations
like removals and moves.

Classes
-------

DocumentFormat
    Abstract base for document formats with render/parse capabilities

Functions
---------

details_document_format()
    Creates format using HTML details blocks and one-line operations
standard_document_format()
    Default document format instance

The document format system supports:
- File listings with complete content in details blocks
- One-line removals in format: Removed: `path/to/file.py`
- One-line moves in format: Moved: `old/path.py` => `new/path.py`
- Diff-compressed listings for space efficiency
- Language detection for syntax highlighting
- Combining multiple formats with | and & operators
"""
from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
import re
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset
from llobot.formats.languages import LanguageGuesser, standard_language_guesser
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.builder import KnowledgeDeltaBuilder
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.text import concat_documents, markdown_code_details, normalize_document

class DocumentFormat:
    """
    Base class for document formats that handle DocumentDelta serialization.

    Document formats can convert DocumentDelta objects to formatted strings
    and parse formatted text back into DocumentDelta objects. They support
    combining via | (union) and & (filtering) operators.
    """

    def render(self, delta: DocumentDelta) -> str | None:
        """
        Renders a DocumentDelta into a string representation.

        Args:
            delta: The document delta to render.

        Returns:
            Formatted string or None if this format cannot handle the delta.
        """
        return None

    def render_fresh(self, path: Path, content: str) -> str | None:
        """Renders a fresh document (new or modified)."""
        return self.render(DocumentDelta(path, content))

    def __call__(self, delta: DocumentDelta) -> str | None:
        return self.render(delta)

    def render_all(self, delta: KnowledgeDelta) -> str:
        """Renders all deltas in a KnowledgeDelta, concatenating results."""
        return concat_documents(*(self.render(d) for d in delta))

    def find(self, message: str) -> list[str]:
        """
        Finds all formatted delta strings in a message.

        Args:
            message: Text to search for formatted deltas.

        Returns:
            List of formatted delta strings found in the message.
        """
        return []

    def parse(self, formatted: str) -> DocumentDelta | None:
        """
        Parses a formatted string back into a DocumentDelta.

        Args:
            formatted: The formatted string to parse.

        Returns:
            DocumentDelta object or None if parsing fails.
        """
        return None

    def parse_message(self, message: str | ChatMessage) -> KnowledgeDelta:
        """Parses all deltas found in a chat message."""
        if isinstance(message, ChatMessage):
            message = message.content

        builder = KnowledgeDeltaBuilder()
        for match in self.find(message):
            delta = self.parse(match)
            if delta:
                builder.add(delta)
        return builder.build()

    def parse_chat(self, chat: ChatBranch) -> KnowledgeDelta:
        """Parses all deltas found in a chat branch."""
        builder = KnowledgeDeltaBuilder()
        for message in chat:
            builder.add(self.parse_message(message.content))
        return builder.build()

    def __or__(self, other: DocumentFormat) -> DocumentFormat:
        """Combines formats with union semantics (try first, then second)."""
        myself = self
        class OrDocumentFormat(DocumentFormat):
            def render(self, delta: DocumentDelta) -> str | None:
                return myself.render(delta) or other.render(delta)
            def find(self, message: str) -> list[str]:
                return myself.find(message) + other.find(message)
            def parse(self, formatted: str) -> DocumentDelta | None:
                delta = myself.parse(formatted)
                if delta:
                    return delta
                return other.parse(formatted)
        return OrDocumentFormat()

    def __and__(self, whitelist: KnowledgeSubset | str) -> DocumentFormat:
        """Filters format to only handle paths in the whitelist."""
        myself = self
        whitelist = coerce_subset(whitelist)
        class AndDocumentFormat(DocumentFormat):
            def render(self, delta: DocumentDelta) -> str | None:
                return myself.render(delta) if delta.path in whitelist else None
            def find(self, message: str) -> list[str]:
                return myself.find(message)
            def parse(self, formatted: str) -> DocumentDelta | None:
                delta = myself.parse(formatted)
                if delta and delta.path not in whitelist:
                    return None
                return delta
        return AndDocumentFormat()

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

# Unified parsing regex for details blocks (handles both File: and Diff: summaries)
_DETAILS_PARSING_RE = re.compile(rf'<details>\n<summary>(File|Diff): ([^\n]+?)</summary>\n\n```+[^\n]*\n(.*)^```+\n\n</details>', re.MULTILINE | re.DOTALL)

# Parsing regexes for one-line operations
_REMOVED_RE = re.compile(_REMOVED_PATTERN, re.MULTILINE)
_MOVED_RE = re.compile(_MOVED_PATTERN, re.MULTILINE)

@lru_cache
def details_document_format(*,
    guesser: LanguageGuesser = standard_language_guesser(),
    quad_backticks: tuple[str, ...] = ('markdown',),
) -> DocumentFormat:
    """
    Create a document format using HTML details blocks and one-line operations.

    This format handles:
    - File listings: <details><summary>File: path</summary>```content```</details>
    - Diff listings: <details><summary>Diff: path</summary>```diff```</details>
    - Removals: Removed: `path/to/file.py`
    - Moves: Moved: `old/path.py` => `new/path.py`

    Args:
        guesser: Language guesser for syntax highlighting
        quad_backticks: Languages requiring 4+ backticks (e.g., when content has markdown)

    Returns:
        DocumentFormat instance
    """
    class DetailsDocumentFormat(DocumentFormat):
        def render(self, delta: DocumentDelta) -> str | None:
            # Handle removals
            if delta.removed:
                return f"Removed: `{delta.path}`"

            # Handle pure moves (no content)
            if delta.moved:
                return f"Moved: `{delta.moved_from}` => `{delta.path}`"

            # Handle file listings with content (regular files or diffs)
            content = delta.content
            if delta.diff:
                summary = f'Diff: {delta.path}'
                lang = 'diff'
            else:
                summary = f'File: {delta.path}'
                lang = guesser(delta.path, content)

            backtick_count = 4 if lang in quad_backticks else 3
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

            # Try parsing details block (File: or Diff:)
            details_match = _DETAILS_PARSING_RE.fullmatch(formatted)
            if details_match:
                block_type, path_str, content = details_match.groups()
                path = Path(path_str.strip())
                content = normalize_document(content)

                if block_type == 'Diff':
                    return DocumentDelta(path, content, diff=True)
                else:  # File:
                    return DocumentDelta(path, content)

            return None

    return DetailsDocumentFormat()

@cache
def standard_document_format() -> DocumentFormat:
    """Get the standard document format instance."""
    return details_document_format()

__all__ = [
    'DocumentFormat',
    'details_document_format',
    'standard_document_format',
]
