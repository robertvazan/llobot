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
        return create_language_guesser(lambda path, content: self(path, content) or other(path, content))

def create_language_guesser(function: Callable[[Path, str], str]) -> LanguageGuesser:
    class LambdaGuesser(LanguageGuesser):
        def guess(self, path: Path, content: str) -> str:
            return function(path, content)
    return LambdaGuesser()

LANGUAGES_BY_EXTENSION = {
    # Documentation and markup
    '.md': 'markdown',
    '.rst': 'rst',
    '.xml': 'xml',
    '.tex': 'latex',

    # Configuration files
    '.toml': 'toml',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.json': 'json',
    '.ini': 'ini',
    '.properties': 'properties',

    # Systems languages
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.hh': 'cpp',
    '.hxx': 'cpp',
    '.rs': 'rust',
    '.go': 'go',
    '.zig': 'zig',
    '.nim': 'nim',

    # Application languages
    '.py': 'python',
    '.java': 'java',
    '.cs': 'csharp',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'jsx',
    '.tsx': 'tsx',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.pl': 'perl',
    '.lua': 'lua',
    '.dart': 'dart',
    '.jl': 'julia',
    '.r': 'r',
    '.R': 'r',
    '.groovy': 'groovy',

    # Functional languages
    '.hs': 'haskell',
    '.ml': 'ocaml',
    '.fs': 'fsharp',
    '.clj': 'clojure',
    '.cljs': 'clojure',
    '.elm': 'elm',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.erl': 'erlang',
    '.hrl': 'erlang',

    # Scientific/Legacy languages
    '.f': 'fortran',
    '.f90': 'fortran',
    '.f95': 'fortran',
    '.f03': 'fortran',
    '.f08': 'fortran',
    '.ada': 'ada',
    '.adb': 'ada',
    '.ads': 'ada',
    '.pas': 'pascal',

    # Web technologies
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.vue': 'vue',
    '.svelte': 'svelte',

    # Scripts
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.bat': 'batch',
    '.cmd': 'batch',
    '.ps1': 'powershell',

    # Data and query languages
    '.sql': 'sql',
    '.graphql': 'graphql',
    '.gql': 'graphql',

    # Build files
    '.mk': 'makefile',
    '.mak': 'makefile',
    '.gradle': 'gradle',
    '.cmake': 'cmake',
    '.sbt': 'scala',
    '.docker': 'dockerfile',
}

@cache
def extension_language_guesser(extensions: dict[str, str] | None = None) -> LanguageGuesser:
    extensions = LANGUAGES_BY_EXTENSION if extensions is None else extensions
    return create_language_guesser(lambda path, content: extensions.get(path.suffix, ''))

LANGUAGES_BY_FILENAME = {
    'Makefile': 'makefile',
    'makefile': 'makefile',
    'CMakeLists.txt': 'cmake',
    'BUILD': 'python',
    'WORKSPACE': 'python',
    'Dockerfile': 'dockerfile',
    'Containerfile': 'dockerfile',
}

@cache
def filename_language_guesser(filenames: dict[str, str] | None = None) -> LanguageGuesser:
    filenames = LANGUAGES_BY_FILENAME if filenames is None else filenames
    return create_language_guesser(lambda path, content: filenames.get(path.name, ''))

@cache
def standard_language_guesser() -> LanguageGuesser:
    return filename_language_guesser() | extension_language_guesser()

__all__ = [
    'LanguageGuesser',
    'create_language_guesser',
    'LANGUAGES_BY_EXTENSION',
    'extension_language_guesser',
    'LANGUAGES_BY_FILENAME',
    'filename_language_guesser',
    'standard_language_guesser',
]
