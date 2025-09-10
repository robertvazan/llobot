"""
Historical knowledge storage.

This package provides interfaces and implementations for storing and retrieving
historical snapshots of knowledge bases.

The main interface is `KnowledgeArchive`. Several implementations are provided:
- tgz: Stores snapshots as compressed tarballs. This is the standard and recommended implementation.
- dummy: A no-op archive that is always empty and ignores writes.
- fs: This submodule provides utilities to save and load knowledge to/from a
  plain directory, but it does not implement the `KnowledgeArchive` interface.

Submodules
----------
dummy
    A no-op knowledge archive.
fs
    Utilities for saving/loading knowledge to/from a directory.
tgz
    A knowledge archive implementation that uses compressed tarballs.
"""
from __future__ import annotations
from datetime import datetime
from functools import lru_cache
import logging
from pathlib import Path
from llobot.utils.zones import Zoning
from llobot.utils.fs import data_home
from llobot.knowledge import Knowledge
from llobot.utils.time import current_time

_logger = logging.getLogger(__name__)

class KnowledgeArchive:
    """
    Base class for knowledge archives.

    A knowledge archive stores timestamped snapshots of a knowledge base.
    """
    def add(self, zone: str, time: datetime, knowledge: Knowledge):
        """
        Adds a new knowledge snapshot to the archive.

        Args:
            zone: The zone (category) to store the snapshot in.
            time: The timestamp for the snapshot.
            knowledge: The knowledge base to store.
        """
        pass

    def remove(self, zone: str, time: datetime):
        """
        Removes a snapshot from the archive.

        Args:
            zone: The zone from which to remove the snapshot.
            time: The timestamp of the snapshot to remove.
        """
        pass

    def last(self, zone: str, cutoff: datetime | None = None) -> Knowledge:
        """
        Retrieves the most recent snapshot from the archive.

        Args:
            zone: The zone to retrieve from.
            cutoff: If provided, only snapshots at or before this time are considered.

        Returns:
            The most recent Knowledge object, or an empty one if none are found.
        """
        return Knowledge()

    def refresh(self, zone: str, knowledge: Knowledge):
        """
        Checks for updates from the source and archives a new snapshot if changes are found.

        Args:
            zone: The zone to store the snapshot in.
            knowledge: The current state of the knowledge.
        """
        fresh = knowledge
        if fresh != self.last(zone):
            self.add(zone, current_time(), fresh)
            _logger.info(f"Refreshed: {zone}")
        else:
            _logger.info(f"Refreshed (no change): {zone}")

@lru_cache
def standard_knowledge_archive(location: Zoning | Path | str = data_home()/'llobot/knowledge') -> KnowledgeArchive:
    """
    Returns the standard knowledge archive, which uses compressed tarballs.

    Args:
        location: The root directory or zoning for the archive.

    Returns:
        The standard knowledge archive.
    """
    from llobot.knowledge.archives.tgz import tgz_knowledge_archive
    return tgz_knowledge_archive(location)

def coerce_knowledge_archive(what: KnowledgeArchive | Zoning | Path | str) -> KnowledgeArchive:
    """
    Coerces the input into a KnowledgeArchive.

    If the input is already a `KnowledgeArchive`, it is returned as is.
    Otherwise, a standard archive is created at the given location.

    Args:
        what: The object to coerce.

    Returns:
        A `KnowledgeArchive` instance.
    """
    if isinstance(what, KnowledgeArchive):
        return what
    else:
        return standard_knowledge_archive(what)

__all__ = [
    'KnowledgeArchive',
    'standard_knowledge_archive',
    'coerce_knowledge_archive',
]
