"""
Formats for converting knowledge and other data structures to readable text.

This package provides various formats that convert llobot's internal data
structures into human-readable and machine-parseable text formats, primarily
for inclusion in LLM prompts and processing of LLM responses.

Submodules
----------

affirmations
    Utilities for creating standard affirmation messages.
documents
    Document formats for rendering and parsing DocumentDelta objects.
    Supports file listings, removals, moves, and diff compression.
knowledge
    Knowledge formats for rendering Knowledge objects and deltas.
    Handles document ordering, filtering, and presentation.
languages
    Language detection for syntax highlighting in code blocks.
    Supports file extension mapping and content-based detection.
mentions
    Parser for @command mentions in chat messages.
prompts
    Prompt formats for assembling complete LLM prompts.
submessages
    Submessage formats for rendering a chat branch into one message.
trees
    Tree formats for hierarchical knowledge presentation.
    Renders directory structures and file hierarchies.

The formats are designed to be composable and configurable, supporting
various output formats and filtering options. They integrate with the
knowledge management system to provide consistent text representations
across the application.

Common patterns:
- Factory functions like standard() provide default configurations
- Many formats support operator overloading (| for union, & for filtering)
- Bidirectional formats can both format and parse their output
"""

__all__ = []
