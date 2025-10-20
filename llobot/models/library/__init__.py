"""
Model libraries for looking up models by key.

This package provides the `ModelLibrary` interface and several implementations
for discovering and retrieving `Model` instances based on a string key.
"""
from __future__ import annotations
from llobot.models import Model

class ModelLibrary:
    """
    Base class for model libraries, which find models based on a key.
    """
    def lookup(self, key: str) -> Model | None:
        """
        Looks up a model that matches the given key.

        Args:
            key: The lookup key, typically a model name.

        Returns:
            A matching `Model` instance, or `None` if not found.
        """
        return None

__all__ = [
    'ModelLibrary',
]
