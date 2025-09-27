from __future__ import annotations
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta

class KnowledgeDeltaBuilder:
    """
    A mutable builder for constructing `KnowledgeDelta` instances.
    """
    _deltas: list[DocumentDelta]

    def __init__(self):
        """
        Initializes an empty `KnowledgeDeltaBuilder`.
        """
        self._deltas = []

    def add(self, delta: DocumentDelta | KnowledgeDelta):
        """
        Adds a document or knowledge delta to the builder.

        If a `KnowledgeDelta` is provided, all of its `DocumentDelta` items
        are added.

        Args:
            delta: The `DocumentDelta` or `KnowledgeDelta` to add.
        """
        if isinstance(delta, DocumentDelta):
            self._deltas.append(delta)
        elif isinstance(delta, KnowledgeDelta):
            self._deltas.extend(delta)
        else:
            raise TypeError(f"Unsupported type for delta: {type(delta)}")

    def build(self) -> KnowledgeDelta:
        """
        Constructs an immutable `KnowledgeDelta` from the current state of the builder.
        """
        return KnowledgeDelta(self._deltas)

__all__ = [
    'KnowledgeDeltaBuilder',
]
