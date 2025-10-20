"""
A model library that is a union of other model libraries.
"""
from __future__ import annotations
from llobot.models import Model
from llobot.models.library import ModelLibrary
from llobot.utils.values import ValueTypeMixin

class UnionModelLibrary(ModelLibrary, ValueTypeMixin):
    """
    A model library that combines multiple libraries, looking them up in order.

    The first library to return a non-`None` model for a given key wins.
    It flattens nested unions for efficiency.
    """
    _libraries: tuple[ModelLibrary, ...]

    def __init__(self, *libraries: ModelLibrary):
        """
        Initializes the union library.

        Args:
            *libraries: The model libraries to combine.
        """
        flattened = []
        for library in libraries:
            if isinstance(library, UnionModelLibrary):
                flattened.extend(library._libraries)
            else:
                flattened.append(library)
        self._libraries = tuple(flattened)

    def lookup(self, key: str) -> Model | None:
        """
        Looks up a model by key in the combined libraries.

        It queries each library in order and returns the first result found.

        Args:
            key: The key of the model to find.

        Returns:
            The `Model` instance if found in any library, otherwise `None`.
        """
        for library in self._libraries:
            model = library.lookup(key)
            if model is not None:
                return model
        return None

__all__ = [
    'UnionModelLibrary',
]
