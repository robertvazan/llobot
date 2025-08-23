from __future__ import annotations
from pathlib import Path

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DocumentDelta):
            return NotImplemented
        return (
            self._path == other._path and
            self._new == other._new and
            self._modified == other._modified and
            self._removed == other._removed and
            self._diff == other._diff and
            self._moved_from == other._moved_from and
            self._content == other._content and
            self._invalid == other._invalid
        )

    def __str__(self) -> str:
        flags = []
        if self.new: flags.append('new')
        if self.modified: flags.append('modified')
        if self.diff: flags.append('diff')
        if self.removed: flags.append('removed')
        if self.moved_from: flags.append(f"moved from {self.moved_from}")
        flag_str = ', '.join(flags)
        return f'{self.path} ({flag_str})'

__all__ = [
    'DocumentDelta',
]
