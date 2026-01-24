"""
Environment component for tracking files loaded into the context.
"""
from __future__ import annotations
import shutil
from pathlib import Path, PurePosixPath
from llobot.environments.persistent import PersistentEnv
from llobot.formats.paths import coerce_path
from llobot.knowledge import Knowledge
from llobot.utils.fs import read_text, write_text

class SeenEnv(PersistentEnv):
    """
    Tracks files that have been loaded into the context.

    This component maintains a mapping from file paths to the content that was
    last loaded into the context. It is used to avoid reloading the same content
    and to enforce safety checks (e.g., preventing edits to files that haven't
    been read).
    """
    _seen: dict[PurePosixPath, str]

    def __init__(self):
        self._seen = {}

    def add(self, path: PurePosixPath | str, content: str):
        """
        Records that a file with the given content has been loaded.

        Args:
            path: The path of the file.
            content: The content of the file.
        """
        self._seen[coerce_path(path)] = content

    def update(self, knowledge: Knowledge):
        """
        Updates the seen environment with all documents from a Knowledge object.
        """
        for path, content in knowledge:
            self._seen[path] = content

    def get(self, path: PurePosixPath | str) -> str | None:
        """
        Gets the content of a file if it has been seen.

        Args:
            path: The path of the file.

        Returns:
            The content if seen, `None` otherwise.
        """
        return self._seen.get(coerce_path(path))

    def __contains__(self, path: PurePosixPath | str) -> bool:
        """
        Checks if a file has been seen.
        """
        return coerce_path(path) in self._seen

    def save(self, directory: Path):
        """
        Saves the seen files to a 'seen' subdirectory.
        """
        root = directory / 'seen'
        if root.exists():
            shutil.rmtree(root)

        for path, content in self._seen.items():
            # Paths are relative (e.g., "src/main.py").
            file_path = root / path
            write_text(file_path, content)

    def load(self, directory: Path):
        """
        Loads the seen files from a 'seen' subdirectory.
        """
        root = directory / 'seen'
        if not root.exists():
            return

        self._seen = {}
        for file in root.rglob('*'):
            if file.is_file():
                try:
                    rel_path = file.relative_to(root)
                    # Validate and coerce path
                    key = coerce_path(rel_path.as_posix())
                    content = read_text(file)
                    self._seen[key] = content
                except Exception:
                    # Ignore unreadable files or invalid paths
                    pass

__all__ = [
    'SeenEnv',
]
