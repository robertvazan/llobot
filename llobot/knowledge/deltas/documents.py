from __future__ import annotations
from pathlib import Path

class DocumentDelta:
    _path: Path
    _content: str | None
    _removed: bool
    _moved_from: Path | None

    def __init__(self,
        path: Path,
        content: str | None,
        *,
        removed: bool = False,
        moved_from: Path | None = None,
    ):
        self._path = path
        self._content = content
        self._removed = removed
        self._moved_from = moved_from
        self._validate()

    def _validate(self):
        """
        Validate that the combination matches one of the three allowed patterns from deltas.md:
        1. File with content (new/modified/original): content required, no flags
        2. Removed file: no content, removed=True, no other flags
        3. Moved file: no content, moved_from set, no other flags
        """
        if self._removed:
            # Pattern 2: Removed file
            if self._content is not None:
                raise ValueError("Removed files cannot have content")
            if self._moved_from is not None:
                raise ValueError("Removed files cannot have other flags")
        elif self._moved_from is not None:
            # Pattern 3: Moved file
            if self._content is not None:
                raise ValueError("Moved files cannot have content")
        else:
            # Pattern 1: Regular file with content
            if self._content is None:
                raise ValueError("Regular files must have content")

    @property
    def path(self) -> Path:
        return self._path

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DocumentDelta):
            return NotImplemented
        return (
            self._path == other._path and
            self._removed == other._removed and
            self._moved_from == other._moved_from and
            self._content == other._content
        )

    def __str__(self) -> str:
        flags = []
        if self.removed: flags.append('removed')
        if self.moved_from: flags.append(f"moved from {self.moved_from}")
        flag_str = ', '.join(flags)
        return f'{self.path} ({flag_str})' if flag_str else str(self.path)

__all__ = [
    'DocumentDelta',
]
