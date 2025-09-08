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
from llobot.models import Model
from llobot.models.streams import ModelStream

class Role:
    _name: str
    _model: Model

    def __init__(self, name: str, model: Model):
        """
        Initializes the Role.

        Args:
            name: The name of the role.
            model: The language model to use.
        """
        self._name = name
        self._model = model

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> Model:
        return self._model

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
