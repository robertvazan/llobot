"""
A model library that uses a dictionary of aliases to look up models.
"""
from __future__ import annotations
from llobot.models import Model
from llobot.models.library import ModelLibrary
from llobot.utils.values import ValueTypeMixin

class AliasedModelLibrary(ModelLibrary, ValueTypeMixin):
    """
    A model library that looks up models using a predefined alias mapping.
    """
    _models: dict[str, Model]

    def __init__(self, models: dict[str, Model]):
        """
        Initializes the library with a dictionary of model aliases.

        Args:
            models: A dictionary mapping string aliases to `Model` instances.
        """
        self._models = dict(models)

    def lookup(self, key: str) -> Model | None:
        """
        Finds a model by its alias.

        Args:
            key: The alias of the model to find.

        Returns:
            The `Model` instance if found, otherwise `None`.
        """
        return self._models.get(key)

__all__ = [
    'AliasedModelLibrary',
]
