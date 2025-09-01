"""
Formatters for converting knowledge and other data structures to readable text.

This package provides various formatters that convert llobot's internal data
structures into human-readable and machine-parseable text formats, primarily
for inclusion in LLM prompts and processing of LLM responses.

Submodules
----------

envelopes
    Envelope formatters for DocumentDelta serialization and parsing
    Supports file listings, removals, moves, and diff compression
knowledge
    Knowledge formatters for rendering Knowledge objects and deltas
    Handles document ordering, filtering, and presentation
languages
    Language detection for syntax highlighting in code blocks
    Supports file extension mapping and content-based detection
prompts
    Prompt formatters for assembling complete LLM prompts
submessages
    Submessage formatters for packing a chat branch into one message
trees
    Tree formatters for hierarchical knowledge presentation
    Renders directory structures and file hierarchies

The formatters are designed to be composable and configurable, supporting
various output formats and filtering options. They integrate with the
knowledge management system to provide consistent text representations
across the application.

Common patterns:
- Factory functions like standard() provide default configurations
- Many formatters support operator overloading (| for union, & for filtering)
- Bidirectional formatters can both format and parse their output
"""

__all__ = []
