from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from pathlib import Path
from llobot.fs.zones import Zoning, coerce_zoning
from llobot.knowledge import Knowledge
from llobot.fs import data_home
from llobot.fs.archives import format_archive_path, last_archive_path
from llobot.knowledge.tgz import KNOWLEDGE_TGZ_SUFFIX, load_knowledge_tgz, save_knowledge_tgz

class KnowledgeArchive:
    def add(self, zone: str, time: datetime, knowledge: Knowledge):
        pass

    def remove(self, zone: str, time: datetime):
        pass

    def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
        return None

@lru_cache(maxsize=2)
def _cached_tgz_load(location: Zoning, zone: str, cutoff: datetime | None) -> Knowledge:
    path = last_archive_path(location[zone], KNOWLEDGE_TGZ_SUFFIX, cutoff)
    return load_knowledge_tgz(path) if path else Knowledge()

@lru_cache
def tgz_knowledge_archive(location: Zoning | Path | str) -> KnowledgeArchive:
    location = coerce_zoning(location)
    class TgzKnowledgeArchive(KnowledgeArchive):
        def _path(self, zone: str, time: datetime):
            return format_archive_path(location[zone], time, KNOWLEDGE_TGZ_SUFFIX)
        def add(self, zone: str, time: datetime, knowledge: Knowledge):
            save_knowledge_tgz(self._path(zone, time), knowledge)
            _cached_tgz_load.cache_clear()
        def remove(self, zone: str, time: datetime):
            self._path(zone, time).unlink(missing_ok=True)
            _cached_tgz_load.cache_clear()
        def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
            return _cached_tgz_load(location, zone, cutoff)
    return TgzKnowledgeArchive()

@lru_cache
def standard_knowledge_archive(location: Zoning | Path | str = data_home()/'llobot/knowledge') -> KnowledgeArchive:
    return tgz_knowledge_archive(location)

def coerce_knowledge_archive(what: KnowledgeArchive | Zoning | Path | str) -> KnowledgeArchive:
    if isinstance(what, KnowledgeArchive):
        return what
    else:
        return standard_knowledge_archive(what)

__all__ = [
    'KnowledgeArchive',
    'tgz_knowledge_archive',
    'standard_knowledge_archive',
    'coerce_knowledge_archive',
]
