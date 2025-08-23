"""
Knowledge delta management for tracking changes between knowledge states.

This module provides comprehensive change tracking for knowledge collections,
including document-level changes, batch operations, and diff compression.

Classes
-------

DocumentDelta
    Individual file change representation with flags for removed/diff/moved_from
KnowledgeDelta
    Collections of document changes with derived properties
KnowledgeDeltaBuilder
    Builder pattern for constructing complex deltas

Functions
---------

fresh()
    Create delta representing fresh knowledge state
between()
    Compute differences between two knowledge states
diff_compress()
    Compress deltas using unified diff format when beneficial

The delta system supports move detection and various derived properties like
touched/present/removed path sets. All DocumentDeltas are valid by construction,
with invalid parameter combinations raising exceptions.

Developer Notes
---------------

The implementation is split across private submodules:

_documents
    DocumentDelta class with validation and change flags
_knowledge
    KnowledgeDelta class with collection operations and derived properties
_builder
    KnowledgeDeltaBuilder class implementing the builder pattern
"""
from __future__ import annotations
from pathlib import Path
import difflib
from llobot.knowledge import Knowledge
from llobot.knowledge.rankings import KnowledgeRanking
from ._documents import DocumentDelta
from ._knowledge import KnowledgeDelta
from ._builder import KnowledgeDeltaBuilder
import llobot.knowledge.rankings

def fresh(knowledge: Knowledge, ranking: KnowledgeRanking | None = None) -> KnowledgeDelta:
    if ranking is None:
        ranking = llobot.knowledge.rankings.standard(knowledge)
    return KnowledgeDelta([DocumentDelta(path, knowledge[path]) for path in ranking if path in knowledge])

def between(before: Knowledge, after: Knowledge, *, move_hints: dict[Path, Path] = {}) -> KnowledgeDelta:
    builder = KnowledgeDeltaBuilder()
    before_paths = before.keys()
    after_paths = after.keys()
    moved = set()

    for path in (after_paths - before_paths).sorted():
        if path in move_hints and move_hints[path] in before_paths and move_hints[path] not in moved:
            source = move_hints[path]
            if before[source] == after[path]:
                builder.add(DocumentDelta(path, None, moved_from=source))
            else:
                # For move with modification, create two separate deltas
                builder.add(DocumentDelta(path, None, moved_from=source))
                builder.add(DocumentDelta(path, after[path]))
            moved.add(source)
        else:
            builder.add(DocumentDelta(path, after[path]))

    for path in (before_paths - after_paths).sorted():
        if path not in moved:
            builder.add(DocumentDelta(path, None, removed=True))

    for path in (before_paths & after_paths).sorted():
        if before[path] != after[path]:
            builder.add(DocumentDelta(path, after[path]))

    return builder.build()

def diff_compress(before: Knowledge, delta: KnowledgeDelta, *, threshold: float = 0.8) -> KnowledgeDelta:
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
    'DocumentDelta',
    'KnowledgeDelta',
    'KnowledgeDeltaBuilder',
    'fresh',
    'between',
    'diff_compress',
]
