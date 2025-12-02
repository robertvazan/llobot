"""
Document format using HTML details blocks.
"""
from __future__ import annotations
from pathlib import Path
from llobot.formats.documents import DocumentFormat
from llobot.formats.languages import LanguageMapping, standard_language_mapping
from llobot.utils.text import markdown_code_details
from llobot.utils.values import ValueTypeMixin

class DetailsDocumentFormat(DocumentFormat, ValueTypeMixin):
    """
    A document format using HTML details blocks.

    This format renders a document as:
    <details><summary>File: path</summary>```content```</details>
    """
    _languages: LanguageMapping
    _quad_backticks: tuple[str, ...]

    def __init__(self, *,
        languages: LanguageMapping = standard_language_mapping(),
        quad_backticks: tuple[str, ...] = ('markdown',),
    ):
        """
        Creates a new details document format.

        Args:
            languages: Language mapping for syntax highlighting.
            quad_backticks: Languages requiring 4+ backticks (e.g., when content has markdown).
        """
        self._languages = languages
        self._quad_backticks = quad_backticks

    def render(self, path: Path, content: str) -> str:
        """
        Renders a document using HTML details/summary tags with a code block inside.
        """
        summary = f'File: {path}'
        lang = self._languages.resolve(path)
        backtick_count = 4 if lang in self._quad_backticks else 3
        return markdown_code_details(summary, lang, content, backtick_count=backtick_count)

__all__ = [
    'DetailsDocumentFormat',
]
