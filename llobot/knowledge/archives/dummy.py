"""
A no-op knowledge archive.
"""
from __future__ import annotations
from datetime import datetime
from functools import cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive

class _DummyKnowledgeArchive(KnowledgeArchive):
    def add(self, zone: Path, time: datetime, knowledge: Knowledge):
        pass

    def remove(self, zone: Path, time: datetime):
        pass

    def last(self, zone: Path, cutoff: datetime | None = None) -> Knowledge:
        return Knowledge()

@cache
def dummy_knowledge_archive() -> KnowledgeArchive:
    """
    Creates a knowledge archive that is always empty and ignores writes.

    Returns:
        A `KnowledgeArchive` instance that performs no operations.
    """
    return _DummyKnowledgeArchive()

__all__ = [
    'dummy_knowledge_archive',
]
