"""
Formats for converting knowledge and other data structures to readable text.

This package provides various formats that convert llobot's internal data
structures into human-readable and machine-parseable text formats, primarily
for inclusion in LLM prompts and processing of LLM responses.

Subpackages
-----------
affirmations
    Utilities for creating standard affirmation messages.
deltas
    Formats for rendering `KnowledgeDelta` and `DocumentDelta` objects.
languages
    Language detection for syntax highlighting in code blocks.
mentions
    Parser for @command mentions in chat messages.
prompts
    Prompt formats for assembling complete LLM prompts.
submessages
    Submessage formats for rendering a chat branch into one message.
indexes
    Formats for hierarchical knowledge presentation.
"""
