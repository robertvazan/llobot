"""
Formats for rendering `KnowledgeDelta` and `DocumentDelta` objects.

This package provides formatters that can serialize knowledge changes into a
human-readable text format suitable for including in LLM prompts, and then
parse the model's response back into structured delta objects.

Submodules
----------
documents
    Defines `DocumentDeltaFormat` for individual file changes.
knowledge
    Defines `KnowledgeDeltaFormat` for collections of document changes.
details
    An implementation of `DocumentDeltaFormat` using HTML `<details>` tags.
chunked
    An implementation of `KnowledgeDeltaFormat` that groups changes into chunks.
granular
    An implementation of `KnowledgeDeltaFormat` that renders each change individually.
"""
