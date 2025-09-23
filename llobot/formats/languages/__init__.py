"""
Language detection from file path for syntax highlighting.

This package provides the `LanguageMapping` base class and several implementations
for detecting the programming or markup language of a file based on its path.
The primary use case is to provide the correct language identifier for syntax
highlighting in Markdown code blocks.

Mappings can be combined using the `|` operator to create a chain of detectors.
The `standard_language_mapping` function provides a default combination that
first checks for specific filenames (e.g., `Makefile`) and then falls back to
file extensions (e.g., `.py`).
"""
from __future__ import annotations
from pathlib import Path

class LanguageMapping:
    """
    Base class for language mappings.
    """
    def resolve(self, path: Path) -> str:
        """
        Resolves the language for a given path.

        An empty string is returned if the language cannot be resolved.

        Args:
            path: The path of the file.

        Returns:
            The language name for syntax highlighting, or an empty string.
        """
        return ''

    def __or__(self, other: LanguageMapping) -> LanguageMapping:
        from llobot.formats.languages.union import LanguageMappingUnion
        return LanguageMappingUnion(self, other)

def standard_language_mapping() -> LanguageMapping:
    """
    Returns the standard language mapping.

    The standard mapping checks for filenames first, then extensions.
    """
    from llobot.formats.languages.extension import ExtensionLanguageMapping
    from llobot.formats.languages.filename import FilenameLanguageMapping
    return FilenameLanguageMapping() | ExtensionLanguageMapping()

__all__ = [
    'LanguageMapping',
    'standard_language_mapping',
]
