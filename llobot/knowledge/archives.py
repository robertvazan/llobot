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

@lru_cache
def tgz(location: Zoning | Path | str) -> KnowledgeArchive:
    location = llobot.fs.zones.coerce(location)
    class TgzKnowledgeArchive(KnowledgeArchive):
        def _path(self, zone: str, time: datetime):
            return llobot.fs.time.path(location[zone], time, llobot.knowledge.tgz.SUFFIX)
        def add(self, zone: str, time: datetime, knowledge: Knowledge):
            llobot.knowledge.tgz.save(self._path(zone, time), knowledge)
        def remove(self, zone: str, time: datetime):
            self._path(zone, time).unlink(missing_ok=True)
        def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
            path = llobot.fs.time.last(location[zone], llobot.knowledge.tgz.SUFFIX, cutoff)
            return llobot.knowledge.tgz.load(path) if path else Knowledge()
    return TgzKnowledgeArchive()

@lru_cache
def cache(uncached: KnowledgeArchive) -> KnowledgeArchive:
    # Only one item is ever stored here, but we still want a dict to avoid mismatches between keys and values.
    cache = {}
    class CachedKnowledgeArchive(KnowledgeArchive):
        def add(self, zone: str, time: datetime, knowledge: Knowledge):
            uncached.add(zone, time, knowledge)
            cache.clear()
        def remove(self, zone: str, time: datetime):
            uncached.remove(zone, time)
            cache.clear()
        def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
            key = (zone, cutoff)
            knowledge = cache.get(key, None)
            if knowledge is None:
                knowledge = uncached.last(zone, cutoff)
                cache.clear()
                cache[key] = knowledge
            return knowledge
    return CachedKnowledgeArchive()

@lru_cache
def standard(location: Zoning | Path | str = llobot.fs.data()/'llobot/knowledge') -> KnowledgeArchive:
    return cache(tgz(location))

def coerce(what: KnowledgeArchive | Zoning | Path | str) -> KnowledgeArchive:
    if isinstance(what, KnowledgeArchive):
        return what
    else:
        return standard(what)

__all__ = [
    'KnowledgeArchive',
    'tgz',
    'cache',
    'standard',
    'coerce',
]

