"""
Llobot core library.

This package contains the core components of Llobot, a library and tool for
building conversational LLM applications.

Subpackages
-----------

chats
    Data structures for representing chat conversations.
commands
    Command and step execution framework for roles.
crammers
    Components for selecting information to fit into a context budget.
environments
    Execution environments for roles to run commands.
formats
    Tools for rendering data structures to readable text for prompts.
knowledge
    A comprehensive system for managing plaintext knowledge bases.
memories
    Memory components for roles.
models
    Integrations with various LLM backends (Ollama, OpenAI, etc.).
projects
    Defines `Project` classes for managing knowledge bases and `ProjectLibrary`
    for looking up projects.
prompts
    Reusable sections for building system prompts.
roles
    Definitions of different bot personalities and capabilities (e.g., Coder).
tools
    File manipulation and system interaction tools for roles.
utils
    Core utilities for text, time, and filesystem operations.

Dependency Order
----------------

The subpackages depend on each other. To avoid circular dependencies and ensure
clean architecture, they are organized in the following order of dependency,
from most fundamental to most dependent. Code in a subpackage should generally
only import from subpackages that appear earlier in this list. Imports from
subpackages that appear later in this list are allowed but should generally be
local imports.

- utils
- chats
- knowledge
- prompts
- formats
- models
- projects
- memories
- crammers
- environments
- tools
- commands
- roles
"""
