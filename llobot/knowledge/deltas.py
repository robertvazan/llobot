from __future__ import annotations
from pathlib import Path
import difflib
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
import llobot.knowledge.rankings

class DocumentDelta:
    _path: Path
    _new: bool
    _modified: bool
    _removed: bool
    _diff: bool
    _moved_from: Path | None
    _content: str | None
    _invalid: bool

    def __init__(self,
        path: Path,
        content: str | None,
        *,
        new: bool = False,
        modified: bool = False,
        removed: bool = False,
        diff: bool = False,
        moved_from: Path | None = None,
        invalid: bool = False,
    ):
        self._path = path
        self._new = new
        self._modified = modified
        self._removed = removed
        self._diff = diff
        self._moved_from = moved_from
        self._content = content
        self._invalid = invalid or not self._check_validity()

    def _check_validity(self) -> bool:
        flags = (self.new, self.modified, self.removed, self.moved, self.diff)
        has_content = self._content is not None

        valid_states = {
            # (new, modified, removed, moved, diff), has_content
            ((False, False, False, False, False), True),   # No flags, with content
            ((True,  False, False, False, False), True),   # new
            ((False, True,  False, False, False), True),   # modified
            ((False, False, True,  False, False), False),  # removed
            ((False, False, False, True,  False), False),  # moved
            ((False, True,  False, True,  False), True),   # modified + moved
            ((False, True,  False, False, True ), True),   # modified + diff
            ((False, True,  False, True,  True ), True),   # modified + diff + moved
        }

        return (flags, has_content) in valid_states

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
    def diff(self) -> bool:
        return self._diff

    @property
    def moved_from(self) -> Path | None:
        return self._moved_from

    @property
    def moved(self) -> bool:
        return self._moved_from is not None

    @property
    def content(self) -> str | None:
        return self._content

    @property
    def valid(self) -> bool:
        return not self._invalid

    def __str__(self) -> str:
        flags = []
        if self.new: flags.append('new')
        if self.modified: flags.append('modified')
        if self.diff: flags.append('diff')
        if self.removed: flags.append('removed')
        if self.moved_from: flags.append(f"moved from {self.moved_from}")
        flag_str = ', '.join(flags)
        return f'{self.path} ({flag_str})'

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

def between(before: Knowledge, after: Knowledge, *, move_hints: dict[Path, Path] = {}) -> KnowledgeDelta:
    builder = KnowledgeDeltaBuilder()
    before_paths = before.keys()
    after_paths = after.keys()
    moved = set()

    for path in (after_paths - before_paths).sorted():
        if path in move_hints and move_hints[path] in before_paths:
            source = move_hints[path]
            if before[source] == after[path]:
                builder.add(DocumentDelta(path, None, moved_from=source))
            else:
                builder.add(DocumentDelta(path, after[path], modified=True, moved_from=source))
            moved.add(source)
        else:
            builder.add(DocumentDelta(path, after[path], new=True))

    for path in (before_paths - after_paths).sorted():
        if path not in moved:
            builder.add(DocumentDelta(path, None, removed=True))

    for path in (before_paths & after_paths).sorted():
        if before[path] != after[path]:
            builder.add(DocumentDelta(path, after[path], modified=True))

    return builder.build()

def diff_compress(before: Knowledge, delta: KnowledgeDelta, *, threshold: float = 0.8) -> KnowledgeDelta:
    builder = KnowledgeDeltaBuilder()
    # At every step, this contains full file content for all paths where that is possible.
    full = dict(before)

    for document in delta:
        # Read old document before we change anything
        path = document.path
        old_content = full.get(path, None)

        # Attempt compression, but do not alter the original document variable
        compressed = document
        if document.valid and document.modified and not document.diff and old_content is not None:
            new_content = document.content
            if old_content == new_content:
                compressed = None
            else:
                diff_lines = list(difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                ))
                diff_lines = diff_lines[2:] # Skip ---/+++ headers
                diff_content = "".join(diff_lines)
                if len(diff_content) < threshold * len(new_content):
                    compressed = DocumentDelta(path, diff_content, modified=True, diff=True, moved_from=document.moved_from)
        if compressed:
            builder.add(compressed)

        # Update the current knowledge using logic similar to 'full' property of KnowledgeDelta
        if not document.valid or document.diff:
            # Conservatively remove content for files when we cannot be sure about it.
            full.pop(document.path, None)
            if document.moved:
                full.pop(document.moved_from, None)
            continue
        if document.moved:
            if document.moved_from in full:
                full[document.path] = full.pop(document.moved_from)
        if document.removed:
            full.pop(document.path, None)
        elif document.content is not None:
            full[document.path] = document.content

    return builder.build()

__all__ = [
    'DocumentDelta',
    'KnowledgeDelta',
    'KnowledgeDeltaBuilder',
    'fresh',
    'between',
    'diff_compress',
]
