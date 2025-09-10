"""
Knowledge delta management for tracking changes between knowledge states.

This package provides comprehensive change tracking for knowledge collections,
including document-level changes, batch operations, and diff compression.

Submodules
----------

documents
    Defines `DocumentDelta` for individual file changes.
knowledge
    Defines `KnowledgeDelta` for collections of document changes.
builder
    Defines `KnowledgeDeltaBuilder` for constructing complex deltas.
diffs
    Provides functions for computing differences between knowledge states.
"""
