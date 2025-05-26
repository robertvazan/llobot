from __future__ import annotations
from functools import cache
from pathlib import Path

class LanguageGuesser:
    # Returns empty string if it cannot guess the language.
    def guess(self, path: Path, content: str) -> str:
        return ''

    def __call__(self, path: Path, content: str) -> str:
        return self.guess(path, content)

    def __or__(self, other: LanguageGuesser) -> LanguageGuesser:
        return create(lambda path, content: self(path, content) or other(path, content))

def create(function: Callable[[Path, str], str]) -> LanguageGuesser:
    class LambdaGuesser(LanguageGuesser):
        def guess(self, path: Path, content: str) -> str:
            return function(path, content)
    return LambdaGuesser()

EXTENSIONS = {
    '.md': 'markdown',
    '.xml': 'xml',
    '.toml': 'toml',
    '.py': 'python',
    '.java': 'java',
    '.rs': 'rust',
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
    '.hh': 'cpp',
    '.hxx': 'cpp',
    '.cxx': 'cpp',
    '.cc': 'cpp',
    '.mak': 'make',
    '.docker': 'dockerfile',
    '.properties': 'properties',
}

@cache
def extension(extensions: dict[str, str] | None = None) -> LanguageGuesser:
    extensions = EXTENSIONS if extensions is None else extensions
    return create(lambda path, content: extensions.get(path.suffix, ''))

FILENAMES = {
    'Makefile': 'make',
    'Dockerfile': 'dockerfile',
    'Containerfile': 'dockerfile',
}

@cache
def filename(filenames: dict[str, str] | None = None) -> LanguageGuesser:
    filenames = FILENAMES if filenames is None else filenames
    return create(lambda path, content: filenames.get(path.name, ''))

@cache
def standard() -> LanguageGuesser:
    return filename() | extension()

__all__ = [
    'LanguageGuesser',
    'create',
    'EXTENSIONS',
    'extensions',
    'FILENAMES',
    'filename',
    'standard',
]

