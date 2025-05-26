from __future__ import annotations
from datetime import datetime
from pathlib import Path
import llobot.time
import llobot.fs

def filename(time: datetime, suffix: str = '') -> Path:
    return Path(llobot.time.format(time) + suffix)

def path(directory: Path | str, time: datetime, suffix: str = '') -> Path:
    return Path(directory)/filename(time, suffix)

def parse(path: Path | str) -> datetime:
    return llobot.time.parse(llobot.fs.stem(path))

def try_parse(path: Path | str) -> datetime | None:
    return llobot.time.try_parse(llobot.fs.stem(path))

def iterate(directory: Path | str, suffix: str = '') -> Iterable[Path]:
    directory = Path(directory)
    if not directory.exists():
        return iter(())
    for path in directory.iterdir():
        if path.name.endswith(suffix) and llobot.time.try_parse(path.name.removesuffix(suffix)):
            yield path

def recent(directory: Path | str, suffix: str = '', cutoff: datetime | None = None) -> list[Path]:
    for path in sorted(iterate(directory, suffix), reverse=True):
        if cutoff is None or llobot.fs.time.parse(path) <= cutoff:
            yield path

def last(directory: Path | str, suffix: str = '', cutoff: datetime | None = None) -> Path | None:
    return next(recent(directory, suffix, cutoff), None)

__all__ = [
    'filename',
    'path',
    'parse',
    'try_parse',
    'iterate',
    'recent',
    'last',
]

