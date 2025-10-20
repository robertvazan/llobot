"""
Model libraries for looking up models by key.

This package provides the `ModelLibrary` interface and several implementations
for discovering and retrieving `Model` instances based on a string key.

Submodules
----------
empty
    An empty model library.
named
    A library that looks up models by name.
aliased
    A library that looks up models by alias.
union
    A library that combines other libraries.
"""
from __future__ import annotations
from llobot.models import Model

class ModelLibrary:
    """
    Base class for model libraries, which find models based on a key.

    Libraries support dictionary-like access via `__getitem__` and can be
    combined using the `|` (`__or__`) operator.
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

    def __getitem__(self, key: str) -> Model:
        """
        Looks up a model by key.

        This provides dictionary-like access to models in the library.

        Args:
            key: The key to look up.

        Returns:
            The matching `Model`.

        Raises:
            KeyError: If no model is found for the given key.
        """
        model = self.lookup(key)
        if model is None:
            raise KeyError(key)
        return model

    def __or__(self, other: ModelLibrary) -> ModelLibrary:
        """
        Combines this library with another.

        Args:
            other: The other `ModelLibrary` to combine with this one.

        Returns:
            A `UnionModelLibrary` that queries this library first, then the other.
        """
        from llobot.models.library.union import UnionModelLibrary
        return UnionModelLibrary(self, other)


__all__ = [
    'ModelLibrary',
]
