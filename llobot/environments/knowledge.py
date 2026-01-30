"""
Environment component for tracking files loaded into the context.
"""
from __future__ import annotations
import shutil
from pathlib import Path, PurePosixPath
from llobot.environments.persistent import PersistentEnv
from llobot.formats.paths import coerce_path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.utils.fs import read_text, write_text

class KnowledgeEnv(PersistentEnv):
    """
    Tracks files that have been loaded into the context.

    This component maintains a mapping from file paths to the content that was
    last loaded into the context. It is used to avoid reloading the same content
    and to enforce safety checks (e.g., preventing edits to files that haven't
    been read).
    """
    _known: dict[PurePosixPath, str]

    def __init__(self):
        self._known = {}

    def add(self, path: PurePosixPath | str, content: str):
        """
        Records that a file with the given content has been loaded.

        Args:
            path: The path of the file.
            content: The content of the file.
        """
        self._known[coerce_path(path)] = content

    def update(self, knowledge: Knowledge):
        """
        Updates the environment with all documents from a Knowledge object.
        """
        for path, content in knowledge:
            self._known[path] = content

    def get(self, path: PurePosixPath | str) -> str | None:
        """
        Gets the content of a file if it is known.

        Args:
            path: The path of the file.

        Returns:
            The content if known, `None` otherwise.
        """
        return self._known.get(coerce_path(path))

    def __contains__(self, path: PurePosixPath | str) -> bool:
        """
        Checks if a file is known.
        """
        return coerce_path(path) in self._known

    def keys(self) -> KnowledgeIndex:
        """
        Returns a KnowledgeIndex of all known file paths.
        """
        return KnowledgeIndex(self._known.keys())

    def save(self, directory: Path):
        """
        Saves the known files to a 'knowledge' subdirectory.
        """
        root = directory / 'knowledge'
        if root.exists():
            shutil.rmtree(root)

        for path, content in self._known.items():
            # Paths are relative (e.g., "src/main.py").
            file_path = root / path
            write_text(file_path, content)

    def load(self, directory: Path):
        """
        Loads the known files from a 'knowledge' subdirectory.
        """
        root = directory / 'knowledge'
        if not root.exists():
            return

        self._known = {}
        for file in root.rglob('*'):
            if file.is_file():
                try:
                    rel_path = file.relative_to(root)
                    # Validate and coerce path
                    key = coerce_path(rel_path.as_posix())
                    content = read_text(file)
                    self._known[key] = content
                except Exception:
                    # Ignore unreadable files or invalid paths
                    pass

__all__ = [
    'KnowledgeEnv',
]
