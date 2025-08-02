from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from pathlib import Path
from llobot.fs.zones import Zoning
from llobot.knowledge import Knowledge
import llobot.time
import llobot.fs
import llobot.fs.zones
import llobot.knowledge.tgz

class KnowledgeArchive:
    def add(self, zone: str, time: datetime, knowledge: Knowledge):
        pass

    def remove(self, zone: str, time: datetime):
        pass

    def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
        return None

@lru_cache(maxsize=2)
def _cached_tgz_load(location: Zoning, zone: str, cutoff: datetime | None) -> Knowledge:
    path = llobot.fs.time.last(location[zone], llobot.knowledge.tgz.SUFFIX, cutoff)
    return llobot.knowledge.tgz.load(path) if path else Knowledge()

@lru_cache
def tgz(location: Zoning | Path | str) -> KnowledgeArchive:
    location = llobot.fs.zones.coerce(location)
    class TgzKnowledgeArchive(KnowledgeArchive):
        def _path(self, zone: str, time: datetime):
            return llobot.fs.time.path(location[zone], time, llobot.knowledge.tgz.SUFFIX)
        def add(self, zone: str, time: datetime, knowledge: Knowledge):
            llobot.knowledge.tgz.save(self._path(zone, time), knowledge)
            _cached_tgz_load.cache_clear()
        def remove(self, zone: str, time: datetime):
            self._path(zone, time).unlink(missing_ok=True)
            _cached_tgz_load.cache_clear()
        def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
            return _cached_tgz_load(location, zone, cutoff)
    return TgzKnowledgeArchive()

@lru_cache
def standard(location: Zoning | Path | str = llobot.fs.data()/'llobot/knowledge') -> KnowledgeArchive:
    return tgz(location)

def coerce(what: KnowledgeArchive | Zoning | Path | str) -> KnowledgeArchive:
    if isinstance(what, KnowledgeArchive):
        return what
    else:
        return standard(what)

__all__ = [
    'KnowledgeArchive',
    'tgz',
    'standard',
    'coerce',
]
