from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
import llobot.knowledge.rankings

class DocumentDelta:
    _path: Path
    _new: bool
    _modified: bool
    _removed: bool
    _moved_from: Path | None
    _content: str | None

    def __init__(self,
        path: Path,
        content: str | None,
        *,
        new: bool = False,
        modified: bool = False,
        removed: bool = False,
        moved_from: Path | None = None,
    ):
        if (new, modified, removed).count(True) > 1:
            raise ValueError("A document can't be new, modified, and removed at the same time.")
        if removed and content is not None:
            raise ValueError("A removed document cannot have content.")
        if moved_from and new:
            raise ValueError("A moved document cannot be marked as new.")
        if moved_from and removed:
            raise ValueError("A moved document cannot be removed in the same delta.")
        if not any((new, modified, removed, moved_from)) and content is None:
            raise ValueError("A document delta must have content or be an edit operation.")

        self._path = path
        self._new = new
        self._modified = modified
        self._removed = removed
        self._moved_from = moved_from
        self._content = content

    @property
    def path(self) -> Path:
        return self._path

    @property
    def new(self) -> bool:
        return self._new

    @property
    def modified(self) -> bool:
        return self._modified

    @property
    def removed(self) -> bool:
        return self._removed

    @property
    def moved_from(self) -> Path | None:
        return self._moved_from

    @property
    def moved(self) -> bool:
        return self._moved_from is not None

    @property
    def content(self) -> str | None:
        return self._content

    def __str__(self) -> str:
        return str(self.path)

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

    def __str__(self) -> str:
        return str(self._deltas)

    def __add__(self, other: KnowledgeDelta) -> KnowledgeDelta:
        if isinstance(other, KnowledgeDelta):
            return KnowledgeDelta(self._deltas + other._deltas)
        return NotImplemented

    @property
    def touched(self) -> KnowledgeIndex:
        paths = set()
        for delta in self._deltas:
            paths.add(delta.path)
            if delta.moved_from:
                paths.add(delta.moved_from)
        return KnowledgeIndex(paths)

    @property
    def present(self) -> KnowledgeIndex:
        paths = set()
        for delta in self._deltas:
            if delta.moved_from:
                paths.discard(delta.moved_from)
            if delta.removed:
                paths.discard(delta.path)
            else:
                paths.add(delta.path)
        return KnowledgeIndex(paths)

    @property
    def removed(self) -> KnowledgeIndex:
        removed = set()
        for delta in self._deltas:
            if delta.moved_from:
                removed.add(delta.moved_from)
            if delta.removed:
                removed.add(delta.path)
            else:
                removed.discard(delta.path)
        return KnowledgeIndex(removed)

    @property
    def full(self) -> Knowledge:
        docs = {}
        for delta in self._deltas:
            if delta.moved_from:
                docs.pop(delta.moved_from, None)
            if delta.removed:
                docs.pop(delta.path, None)
            elif delta.content is not None:
                docs[delta.path] = delta.content
        return Knowledge(docs)

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

def fresh(knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> KnowledgeDelta:
    if ranking is None:
        ranking = llobot.knowledge.rankings.lexicographical(knowledge)
    return KnowledgeDelta([DocumentDelta(path, knowledge[path]) for path in ranking if path in knowledge])

__all__ = [
    'DocumentDelta',
    'KnowledgeDelta',
    'KnowledgeDeltaBuilder',
    'fresh',
]
