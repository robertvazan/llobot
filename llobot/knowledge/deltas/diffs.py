"""
Functions for computing differences between knowledge states.
"""
from __future__ import annotations
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.builder import KnowledgeDeltaBuilder

def knowledge_delta_between(before: Knowledge, after: Knowledge) -> KnowledgeDelta:
    """Computes differences between two knowledge states."""
    builder = KnowledgeDeltaBuilder()
    before_paths = before.keys()
    after_paths = after.keys()

    for path in (before_paths - after_paths).sorted():
        builder.add(DocumentDelta(path, None, removed=True))

    for path in (after_paths - before_paths).sorted():
        builder.add(DocumentDelta(path, after[path]))

    for path in (before_paths & after_paths).sorted():
        if before[path] != after[path]:
            builder.add(DocumentDelta(path, after[path]))

    return builder.build()

__all__ = [
    'knowledge_delta_between',
]
