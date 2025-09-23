"""
Union of language mappings.
"""
from __future__ import annotations
from pathlib import Path
from llobot.formats.languages import LanguageMapping
from llobot.utils.values import ValueTypeMixin

class LanguageMappingUnion(LanguageMapping, ValueTypeMixin):
    """
    A language mapping that combines multiple mappings in order.
    """
    _mappings: tuple[LanguageMapping, ...]

    def __init__(self, *mappings: LanguageMapping):
        """
        Creates a new union of language mappings.

        Args:
            *mappings: The language mappings to combine.
        """
        flattened = []
        for mapping in mappings:
            if isinstance(mapping, LanguageMappingUnion):
                flattened.extend(mapping._mappings)
            else:
                flattened.append(mapping)
        self._mappings = tuple(flattened)

    def resolve(self, path: Path) -> str:
        """
        Resolves the language by trying each mapping in order.

        Args:
            path: The path of the file.

        Returns:
            The first language name resolved by any of the mappings, or an empty string.
        """
        for mapping in self._mappings:
            language = mapping.resolve(path)
            if language:
                return language
        return ''

__all__ = [
    'LanguageMappingUnion',
]
