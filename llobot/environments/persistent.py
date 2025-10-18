"""
Persistent environment components.
"""
from __future__ import annotations
from pathlib import Path

class PersistentEnv:
    """
    An interface for environment components that can be saved to and loaded from disk.
    """
    def save(self, directory: Path):
        """
        Saves the component's state to a file within the given directory.

        Args:
            directory: The directory to save the state into.
        """
        raise NotImplementedError

    def load(self, directory: Path):
        """
        Loads the component's state from a file within the given directory.

        If the file doesn't exist, the component should remain in its default state.

        Args:
            directory: The directory to load the state from.
        """
        raise NotImplementedError

__all__ = [
    'PersistentEnv',
]
