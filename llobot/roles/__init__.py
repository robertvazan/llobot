"""
Definitions of different bot personalities and capabilities.

This package defines the `Role` class, which encapsulates the logic for
assembling the context for a large language model. Each role has an associated
model and defines how to "stuff" the context with system prompts, knowledge,
and examples.

Submodules
----------

chatbot
    A simple chatbot role.
imitator
    An imitator role that learns from examples.
coder
    A role specialized for software development tasks.
editor
    A role for editing and analyzing files, serving as a base for Coder.
models
    A wrapper that exposes a `Role` as a `Model`.

Markdown files like `coder.md` and `editor.md` contain the core system
prompts for the respective roles.
"""

from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.models.streams import ModelStream

class Role:
    @property
    def name(self) -> str:
        """The name of the role."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    def chat(self, prompt: ChatBranch) -> ModelStream:
        """
        Processes user's prompt and returns response as a stream.

        Args:
            prompt: The user's prompt as a chat branch.

        Returns:
            A model stream with the generated response.
        """
        raise NotImplementedError

__all__ = [
    'Role',
]
