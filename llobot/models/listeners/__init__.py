"""
Listeners that expose llobot models via standard protocols (Ollama, OpenAI).

This package provides `ModelListener` implementations that run an HTTP server
to make a collection of llobot `Model` instances available to any client that
speaks the Ollama or OpenAI protocols.

Submodules
----------
ollama
    An Ollama-compatible listener.
openai
    An OpenAI-compatible listener.
"""
from __future__ import annotations

class ModelListener:
    """
    Base class for model listeners.
    """
    def listen(self):
        """
        Starts the listener and blocks forever.
        """
        raise NotImplementedError

__all__ = [
    'ModelListener',
]
