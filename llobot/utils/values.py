from __future__ import annotations
from typing import Any, Iterable

class ValueTypeMixin:
    """
    A mixin for value types that provides default __eq__, __hash__, and __repr__.

    This mixin implements these methods based on the instance's attributes,
    excluding any fields marked as ephemeral.
    """
    def _ephemeral_fields(self) -> Iterable[str]:
        """
        Returns a list of fields that are ignored in __eq__, __hash__, and __repr__.

        This is useful for caches and other ephemeral data. By default, no fields
        are considered ephemeral.
        """
        return []

    def _value_fields(self) -> dict[str, Any]:
        """
        Returns a dict of fields to be used in __eq__, __hash__, and __repr__.
        """
        ephemeral = set(self._ephemeral_fields())
        return {k: v for k, v in vars(self).items() if k not in ephemeral}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._value_fields() == other._value_fields()

    def __hash__(self) -> int:
        # Sort items to ensure hash is order-independent
        return hash(tuple(sorted(self._value_fields().items())))

    def __repr__(self) -> str:
        # Sort items for consistent representation
        fields = ", ".join(f"{k}={v!r}" for k, v in sorted(self._value_fields().items()))
        return f"{self.__class__.__name__}({fields})"

__all__ = [
    'ValueTypeMixin',
]
