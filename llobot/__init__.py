"""
Llobot core library.

This package contains the core components of Llobot, a library and tool for
building conversational LLM applications.

Subpackages
-----------

chats
    Data structures for representing chat conversations.
crammers
    Components for selecting information to fit into a context budget.
environments
    Execution environments for roles to run commands.
formatters
    Tools for converting data structures to readable text for prompts.
fs
    Filesystem utilities for data and cache management.
knowledge
    A comprehensive system for managing plaintext knowledge bases.
models
    Integrations with various LLM backends (Ollama, OpenAI, etc.).
prompts
    Reusable sections for building system prompts.
roles
    Definitions of different bot personalities and capabilities (e.g., Coder).
scrapers
    Tools to build knowledge graphs from source code and other documents.

Modules
-------

projects
    Defines the `Project` class for managing knowledge bases.
text
    Provides text manipulation utilities.
time
    Utilities for handling timestamps.
"""
