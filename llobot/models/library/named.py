"""
A model library that looks up models by name from a fixed collection.
"""
from __future__ import annotations
from llobot.models import Model
from llobot.models.library import ModelLibrary
from llobot.utils.values import ValueTypeMixin

class NamedModelLibrary(ModelLibrary, ValueTypeMixin):
    """
    A model library that looks up models by name from a pre-defined collection.
    """
    _models: dict[str, Model]

    def __init__(self, *models: Model):
        """
        Initializes the library with a collection of models.

        Args:
            *models: The models to include in the library.

        Raises:
            ValueError: If there are models with duplicate names.
        """
        self._models = {}
        for model in models:
            if model.name in self._models:
                raise ValueError(f"Duplicate model name: {model.name}")
            self._models[model.name] = model

    def lookup(self, key: str) -> Model | None:
        """
        Finds a model by its name.

        Args:
            key: The name of the model to find.

        Returns:
            The `Model` instance if found, otherwise `None`.
        """
        return self._models.get(key)

__all__ = [
    'NamedModelLibrary',
]
