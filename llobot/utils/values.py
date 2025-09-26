from __future__ import annotations
from typing import Any, Iterable

class ValueTypeMixin:
    """
    A mixin for value types that provides default __eq__, __hash__, and __repr__.

    This mixin implements these methods based on the instance's attributes,
    excluding any fields marked as ephemeral. Leading underscores are stripped
    from attribute names, allowing private fields to be part of the value.
    The hash code is cached for performance. Equality comparison is optimized
    with an initial identity and hash check, falling back to full attribute
    comparison if the object is not hashable.
    """
    _hash: int | None

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
        ephemeral.add('_hash')
        # Strip leading underscores from private fields to make them part of the value.
        return {k.lstrip('_'): v for k, v in vars(self).items() if k not in ephemeral}

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return NotImplemented
        try:
            if hash(self) != hash(other):
                return False
        except TypeError:
            # Not hashable, fall back to full comparison.
            pass
        return self._value_fields() == other._value_fields()

    def __hash__(self) -> int:
        """
        Calculates and caches the hash code.
        """
        if not hasattr(self, '_hash') or self._hash is None:
            items = []
            for k, v in self._value_fields().items():
                if isinstance(v, dict):
                    items.append((k, frozenset(v.items())))
                else:
                    items.append((k, v))
            # Sort items to ensure hash is order-independent
            self._hash = hash(tuple(sorted(items)))
        return self._hash

    def __repr__(self) -> str:
        # Sort items for consistent representation
        fields = ", ".join(f"{k}={v!r}" for k, v in sorted(self._value_fields().items()))
        return f"{self.__class__.__name__}({fields})"

__all__ = [
    'ValueTypeMixin',
]
