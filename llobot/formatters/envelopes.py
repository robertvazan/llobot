"""
Envelope formatters for knowledge deltas.

This module provides formatters that can serialize DocumentDelta objects into
readable text formats and parse them back. The primary formatter uses HTML
details blocks for file listings and simple one-line formats for operations
like removals and moves.

Classes
-------

EnvelopeFormatter
    Abstract base for envelope formatters with format/parse capabilities

Functions
---------

details_envelopes()
    Creates formatter using HTML details blocks and one-line operations
standard_envelopes()
    Default envelope formatter instance

The envelope system supports:
- File listings with complete content in details blocks
- One-line removals in format: Removed: `path/to/file.py`
- One-line moves in format: Moved: `old/path.py` => `new/path.py`
- Diff-compressed listings for space efficiency
- Language detection for syntax highlighting
- Combining multiple formatters with | and & operators
"""
from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
import re
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset
from llobot.formatters.languages import LanguageGuesser, standard_language_guesser
from llobot.knowledge.deltas import DocumentDelta, KnowledgeDelta, KnowledgeDeltaBuilder
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.text import concat_documents, markdown_code_details, normalize_document

class EnvelopeFormatter:
    """
    Base class for envelope formatters that handle DocumentDelta serialization.

    Envelope formatters can convert DocumentDelta objects to formatted strings
    and parse formatted text back into DocumentDelta objects. They support
    combining via | (union) and & (filtering) operators.
    """

    def format(self, delta: DocumentDelta) -> str | None:
        """
        Format a DocumentDelta into a string representation.

        Args:
            delta: The document delta to format

        Returns:
            Formatted string or None if this formatter cannot handle the delta
        """
        return None

    def __call__(self, delta: DocumentDelta) -> str | None:
        return self.format(delta)

    def format_all(self, delta: KnowledgeDelta) -> str:
        """Format all deltas in a KnowledgeDelta, concatenating results."""
        return concat_documents(*(self.format(d) for d in delta))

    def find(self, message: str) -> list[str]:
        """
        Find all formatted delta strings in a message.

        Args:
            message: Text to search for formatted deltas

        Returns:
            List of formatted delta strings found in the message
        """
        return []

    def parse(self, formatted: str) -> DocumentDelta | None:
        """
        Parse a formatted string back into a DocumentDelta.

        Args:
            formatted: The formatted string to parse

        Returns:
            DocumentDelta object or None if parsing fails
        """
        return None

    def parse_message(self, message: str | ChatMessage) -> KnowledgeDelta:
        """Parse all deltas found in a chat message."""
        if isinstance(message, ChatMessage):
            message = message.content

        builder = KnowledgeDeltaBuilder()
        for match in self.find(message):
            delta = self.parse(match)
            if delta:
                builder.add(delta)
        return builder.build()

    def parse_chat(self, chat: ChatBranch) -> KnowledgeDelta:
        """Parse all deltas found in a chat branch."""
        builder = KnowledgeDeltaBuilder()
        for message in chat:
            builder.add(self.parse_message(message.content))
        return builder.build()

    def __or__(self, other: EnvelopeFormatter) -> EnvelopeFormatter:
        """Combine formatters with union semantics (try first, then second)."""
        myself = self
        class OrEnvelopeFormatter(EnvelopeFormatter):
            def format(self, delta: DocumentDelta) -> str | None:
                return myself.format(delta) or other.format(delta)
            def find(self, message: str) -> list[str]:
                return myself.find(message) + other.find(message)
            def parse(self, formatted: str) -> DocumentDelta | None:
                delta = myself.parse(formatted)
                if delta:
                    return delta
                return other.parse(formatted)
        return OrEnvelopeFormatter()

    def __and__(self, whitelist: KnowledgeSubset | str) -> EnvelopeFormatter:
        """Filter formatter to only handle paths in the whitelist."""
        myself = self
        whitelist = coerce_subset(whitelist)
        class AndEnvelopeFormatter(EnvelopeFormatter):
            def format(self, delta: DocumentDelta) -> str | None:
                return myself.format(delta) if delta.path in whitelist else None
            def find(self, message: str) -> list[str]:
                return myself.find(message)
            def parse(self, formatted: str) -> DocumentDelta | None:
                delta = myself.parse(formatted)
                if delta and delta.path not in whitelist:
                    return None
                return delta
        return AndEnvelopeFormatter()

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
def details_envelopes(*,
    guesser: LanguageGuesser = standard_language_guesser(),
    quad_backticks: tuple[str, ...] = ('markdown',),
) -> EnvelopeFormatter:
    """
    Create an envelope formatter using HTML details blocks and one-line operations.

    This formatter handles:
    - File listings: <details><summary>File: path</summary>```content```</details>
    - Diff listings: <details><summary>Diff: path</summary>```diff```</details>
    - Removals: Removed: `path/to/file.py`
    - Moves: Moved: `old/path.py` => `new/path.py`

    Args:
        guesser: Language guesser for syntax highlighting
        quad_backticks: Languages requiring 4+ backticks (e.g., when content has markdown)

    Returns:
        EnvelopeFormatter instance
    """
    class DetailsEnvelopeFormatter(EnvelopeFormatter):
        def format(self, delta: DocumentDelta) -> str | None:
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

    return DetailsEnvelopeFormatter()

@cache
def standard_envelopes() -> EnvelopeFormatter:
    """Get the standard envelope formatter instance."""
    return details_envelopes()

__all__ = [
    'EnvelopeFormatter',
    'details_envelopes',
    'standard_envelopes',
]
