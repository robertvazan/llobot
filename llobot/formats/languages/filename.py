"""
Language mapping based on filename.
"""
from __future__ import annotations
from pathlib import Path
from llobot.formats.languages import LanguageMapping
from llobot.utils.values import ValueTypeMixin

LANGUAGES_BY_FILENAME = {
    'Makefile': 'makefile',
    'makefile': 'makefile',
    'CMakeLists.txt': 'cmake',
    'BUILD': 'python',
    'WORKSPACE': 'python',
    'Dockerfile': 'dockerfile',
    'Containerfile': 'dockerfile',
}

class FilenameLanguageMapping(LanguageMapping, ValueTypeMixin):
    """
    A language mapping based on filenames.
    """
    _filenames: dict[str, str]

    def __init__(self, filenames: dict[str, str] | None = None):
        """
        Creates a new filename-based language mapping.

        Args:
            filenames: A dictionary mapping filenames to language names.
                       Defaults to a standard set of filenames.
        """
        self._filenames = LANGUAGES_BY_FILENAME if filenames is None else filenames

    def resolve(self, path: Path) -> str:
        """
        Resolves the language from the file's name.

        Args:
            path: The path of the file.

        Returns:
            The language name, or an empty string if the filename is not found.
        """
        return self._filenames.get(path.name, '')

__all__ = [
    'LANGUAGES_BY_FILENAME',
    'FilenameLanguageMapping',
]
