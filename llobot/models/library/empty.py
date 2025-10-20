"""
An empty model library.
"""
from __future__ import annotations
from llobot.models.library import ModelLibrary
from llobot.models import Model
from llobot.utils.values import ValueTypeMixin

class EmptyModelLibrary(ModelLibrary, ValueTypeMixin):
    """
    A model library that contains no models and always returns `None`.
    """
    def lookup(self, key: str) -> Model | None:
        return None

__all__ = [
    'EmptyModelLibrary',
]
