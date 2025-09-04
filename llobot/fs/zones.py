from __future__ import annotations
from functools import cache
from pathlib import Path
from typing import Callable

class Zoning:
    def resolve(self, zone: str) -> Path:
        raise NotImplementedError

    def __getitem__(self, zone: str) -> Path:
        return self.resolve(zone)

def create_zoning(resolve: Callable[[str], Path]) -> Zoning:
    class LambdaZoning(Zoning):
        def resolve(self, zone: str) -> Path:
            return resolve(zone)
    return LambdaZoning()

@cache
def prefix_zoning(prefix: Path | str) -> Zoning:
    prefix = Path(prefix).expanduser()
    return create_zoning(lambda zone: prefix / zone)

@cache
def wildcard_zoning(pattern: Path | str) -> Zoning:
    pattern = Path(pattern).expanduser()
    if '*' not in str(pattern):
        raise ValueError
    return create_zoning(lambda zone: Path(*(part.replace('*', zone) for part in pattern.parts)))

def coerce_zoning(what: Zoning | Path | str) -> Zoning:
    if isinstance(what, Zoning):
        return what
    elif '*' in str(what):
        return wildcard_zoning(what)
    else:
        return prefix_zoning(what)

__all__ = [
    'Zoning',
    'create_zoning',
    'prefix_zoning',
    'wildcard_zoning',
    'coerce_zoning',
]
