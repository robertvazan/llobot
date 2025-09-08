"""
Functions for compressing knowledge deltas.
"""
from __future__ import annotations
import difflib
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.builder import KnowledgeDeltaBuilder

def compress_knowledge_delta(before: Knowledge, delta: KnowledgeDelta, *, threshold: float = 0.8) -> KnowledgeDelta:
    """Compresses deltas using unified diff format when beneficial."""
    builder = KnowledgeDeltaBuilder()
    # At every step, this contains full file content for all paths where that is possible.
    full = dict(before)

    for document in delta:
        # Read old document before we change anything
        path = document.path
        old_content = full.get(path, None)

        # Attempt compression, but do not alter the original document variable
        compressed = document
        if document.content is not None and not document.diff and old_content is not None:
            new_content = document.content
            if old_content == new_content:
                compressed = None
            else:
                diff_lines = list(difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                ))
                diff_lines = diff_lines[2:] # Skip ---/+++ headers
                diff_content = "".join(diff_lines)
                if len(diff_content) < threshold * len(new_content):
                    compressed = DocumentDelta(path, diff_content, diff=True)
        if compressed:
            builder.add(compressed)

        # Update the current knowledge
        if document.diff:
            # Remove content for diff files since we cannot be sure about it
            full.pop(document.path, None)
            if document.moved:
                full.pop(document.moved_from, None)
            continue
        if document.moved:
            if document.moved_from in full:
                full[document.path] = full.pop(document.moved_from)
        if document.removed:
            full.pop(document.path, None)
        elif document.content is not None:
            full[document.path] = document.content

    return builder.build()

__all__ = [
    'compress_knowledge_delta',
]
