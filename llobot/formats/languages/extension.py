"""
Language mapping based on file extension.
"""
from __future__ import annotations
from pathlib import Path
from llobot.formats.languages import LanguageMapping
from llobot.utils.values import ValueTypeMixin

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

class ExtensionLanguageMapping(LanguageMapping, ValueTypeMixin):
    """
    A language mapping based on file extensions.
    """
    _extensions: dict[str, str]

    def __init__(self, extensions: dict[str, str] | None = None):
        """
        Creates a new extension-based language mapping.

        Args:
            extensions: A dictionary mapping extensions to language names.
                        Defaults to a standard set of extensions.
        """
        self._extensions = LANGUAGES_BY_EXTENSION if extensions is None else extensions

    def resolve(self, path: Path) -> str:
        """
        Resolves the language from the file's suffix.

        Args:
            path: The path of the file.

        Returns:
            The language name, or an empty string if the suffix is not found.
        """
        return self._extensions.get(path.suffix, '')

__all__ = [
    'LANGUAGES_BY_EXTENSION',
    'ExtensionLanguageMapping',
]
