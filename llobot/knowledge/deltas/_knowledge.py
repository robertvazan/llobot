from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from ._documents import DocumentDelta

class KnowledgeDelta:
    _deltas: list[DocumentDelta]

    def __init__(self, deltas: Iterable[DocumentDelta] = []):
        self._deltas = list(deltas)

    def __bool__(self) -> bool:
        return bool(self._deltas)

    def __len__(self) -> int:
        return len(self._deltas)

    def __iter__(self) -> Iterator[DocumentDelta]:
        return iter(self._deltas)

    def __getitem__(self, key: int | slice) -> DocumentDelta | KnowledgeDelta:
        if isinstance(key, slice):
            return KnowledgeDelta(self._deltas[key])
        return self._deltas[key]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KnowledgeDelta):
            return NotImplemented
        return self._deltas == other._deltas

    def __str__(self) -> str:
        return '[' + ', '.join(str(d) for d in self) + ']'

    def __add__(self, other: KnowledgeDelta) -> KnowledgeDelta:
        if isinstance(other, KnowledgeDelta):
            return KnowledgeDelta(self._deltas + other._deltas)
        return NotImplemented

    @property
    def touched(self) -> KnowledgeIndex:
        paths = set()
        for delta in self:
            paths.add(delta.path)
            if delta.moved_from:
                paths.add(delta.moved_from)
        return KnowledgeIndex(paths)

    @property
    def present(self) -> KnowledgeIndex:
        """
        Returns an index of documents that are known to be present after applying this delta.
        """
        paths = set()
        for delta in self:
            # Move sources are processed even for invalid document deltas,
            # because removal is conservative considering the objective of this property.
            if delta.moved:
                paths.discard(delta.moved_from)
            # If a document delta is invalid, we cannot be sure what really happened.
            # Since this property requires certainty, we treat invalid deltas as removals.
            if delta.removed or not delta.valid:
                paths.discard(delta.path)
            else:
                paths.add(delta.path)
        return KnowledgeIndex(paths)

    @property
    def removed(self) -> KnowledgeIndex:
        """
        Returns an index of documents that are known to be removed after applying this delta.
        """
        paths = set()
        for delta in self:
            if delta.valid:
                if delta.moved:
                    paths.add(delta.moved_from)
                if delta.removed:
                    paths.add(delta.path)
                else:
                    paths.discard(delta.path)
            else:
                # If the document delta is invalid, we cannot be sure what happened.
                # Since this property requires certainty, we conservatively assume the files might still exist.
                paths.discard(delta.path)
                if delta.moved:
                    paths.discard(delta.moved_from)
        return KnowledgeIndex(paths)

    @property
    def full(self) -> Knowledge:
        """
        Returns the full content of all documents whose state is fully known after the delta.
        Deltas that are invalid, represent a diff, or are removals do not contribute content.
        """
        docs = {}
        for delta in self:
            if not delta.valid or delta.diff:
                # Conservatively remove content for files when we cannot be sure about it.
                docs.pop(delta.path, None)
                if delta.moved:
                    docs.pop(delta.moved_from, None)
                continue
            if delta.moved:
                if delta.moved_from in docs:
                    docs[delta.path] = docs.pop(delta.moved_from)
            if delta.removed:
                docs.pop(delta.path, None)
            elif delta.content is not None:
                docs[delta.path] = delta.content
        return Knowledge(docs)

    @property
    def moves(self) -> dict[Path, Path]:
        """
        Traces down original paths for document deltas that have 'move from' flags.
        """
        moves = {}
        for delta in self:
            if delta.moved:
                source = delta.moved_from
                if source in moves:
                    source = moves[source]
                moves[delta.path] = source
        return moves

__all__ = [
    'KnowledgeDelta',
]
