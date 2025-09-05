"""
A knowledge archive implementation that uses compressed tarballs.
"""
from __future__ import annotations
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import io
import tarfile
from llobot.fs import write_bytes
from llobot.fs.archives import format_archive_path, last_archive_path
from llobot.fs.zones import Zoning, coerce_zoning
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.text import normalize_document

KNOWLEDGE_TGZ_SUFFIX = '.tar.gz'

def serialize_knowledge_tgz(knowledge: Knowledge) -> bytes:
    """
    Serializes a knowledge base into a compressed tarball in memory.

    Args:
        knowledge: The knowledge base to serialize.

    Returns:
        The serialized knowledge as bytes.
    """
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
        for path in knowledge.keys().sorted():
            content = knowledge[path].encode('utf-8')
            info = tarfile.TarInfo(path.as_posix())
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()

def deserialize_knowledge_tgz(buffer: bytes) -> Knowledge:
    """
    Deserializes a knowledge base from a compressed tarball in memory.

    Args:
        buffer: The bytes of the compressed tarball.

    Returns:
        The deserialized knowledge base.
    """
    knowledge = {}
    with tarfile.open(fileobj=io.BytesIO(buffer), mode='r:gz') as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            content = normalize_document(tar.extractfile(member).read().decode('utf-8'))
            knowledge[Path(member.name)] = content
    return Knowledge(knowledge)

def save_knowledge_tgz(path: Path, knowledge: Knowledge):
    """
    Saves a knowledge base to a compressed tarball file.

    Args:
        path: The path to save the file to.
        knowledge: The knowledge base to save.
    """
    write_bytes(path, serialize_knowledge_tgz(knowledge))

@lru_cache(maxsize=2)
def load_knowledge_tgz(path: Path) -> Knowledge:
    """
    Loads a knowledge base from a compressed tarball file.

    This function's results are cached.

    Args:
        path: The path to the compressed tarball.

    Returns:
        The loaded knowledge base.
    """
    return deserialize_knowledge_tgz(path.read_bytes())

@lru_cache
def tgz_knowledge_archive(location: Zoning | Path | str) -> KnowledgeArchive:
    """
    Creates a knowledge archive that stores snapshots as compressed tarballs.

    Args:
        location: The root directory or zoning for the archive.

    Returns:
        A `KnowledgeArchive` instance that uses tgz files for storage.
    """
    location = coerce_zoning(location)
    class TgzKnowledgeArchive(KnowledgeArchive):
        def _path(self, zone: str, time: datetime):
            return format_archive_path(location[zone], time, KNOWLEDGE_TGZ_SUFFIX)
        def add(self, zone: str, time: datetime, knowledge: Knowledge):
            save_knowledge_tgz(self._path(zone, time), knowledge)
            load_knowledge_tgz.cache_clear()
        def remove(self, zone: str, time: datetime):
            self._path(zone, time).unlink(missing_ok=True)
            load_knowledge_tgz.cache_clear()
        def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
            path = last_archive_path(location[zone], KNOWLEDGE_TGZ_SUFFIX, cutoff)
            return load_knowledge_tgz(path) if path else Knowledge()
    return TgzKnowledgeArchive()

__all__ = [
    'KNOWLEDGE_TGZ_SUFFIX',
    'serialize_knowledge_tgz',
    'deserialize_knowledge_tgz',
    'save_knowledge_tgz',
    'load_knowledge_tgz',
    'tgz_knowledge_archive',
]
