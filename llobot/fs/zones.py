from __future__ import annotations
from functools import cache
from pathlib import Path

class Zoning:
    def resolve(self, zone: str) -> Path:
        raise NotImplementedError

    def __getitem__(self, zone: str) -> Path:
        return self.resolve(zone)

def create(resolve: Callable[[str], Path]) -> Zoning:
    class LambdaZoning(Zoning):
        def resolve(self, zone: str) -> Path:
            return resolve(zone)
    return LambdaZoning()

@cache
def prefix(prefix: Path | str) -> Zoning:
    prefix = Path(prefix).expanduser()
    return create(lambda zone: prefix / zone)

@cache
def wildcard(pattern: Path | str) -> Zoning:
    pattern = Path(pattern).expanduser()
    if '*' not in str(pattern):
        raise ValueError
    return create(lambda zone: Path(*(part.replace('*', zone) for part in pattern.parts)))

def coerce(what: Zoning | Path | str) -> Zoning:
    if isinstance(what, Zoning):
        return what
    elif '*' in str(what):
        return wildcard(what)
    else:
        return prefix(what)

__all__ = [
    'Zoning',
    'create',
    'prefix',
    'wildcard',
    'coerce',
]
