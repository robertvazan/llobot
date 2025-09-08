from __future__ import annotations
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta

class KnowledgeDeltaBuilder:
    _deltas: list[DocumentDelta]

    def __init__(self):
        self._deltas = []

    def add(self, delta: DocumentDelta | KnowledgeDelta):
        if isinstance(delta, DocumentDelta):
            self._deltas.append(delta)
        elif isinstance(delta, KnowledgeDelta):
            self._deltas.extend(delta)
        else:
            raise TypeError(f"Unsupported type for delta: {type(delta)}")

    def build(self) -> KnowledgeDelta:
        return KnowledgeDelta(self._deltas)

__all__ = [
    'KnowledgeDeltaBuilder',
]
