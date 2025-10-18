"""
Integrations with various LLM backends (Ollama, OpenAI, etc.).

This package defines the base `Model` class that all backend model integrations
implement. Each implementation handles communication with a specific LLM API
(e.g., Anthropic, Gemini, Ollama, OpenAI).

Models are immutable value types. They are configured at instantiation time.

Subpackages
-----------
listeners
    Servers that expose llobot models via standard protocols (Ollama, OpenAI).
ollama
    Client for Ollama-compatible models.

Submodules
----------
anthropic
    Client for Anthropic (Claude) models.
echo
    An echo model for testing and debugging.
gemini
    Client for Google Gemini models.
openai
    Client for OpenAI models.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.stream import ChatStream

class Model:
    """
    Base class for all language models.
    """
    @property
    def name(self) -> str:
        """A unique name for the model within llobot."""
        raise NotImplementedError

    @property
    def context_budget(self) -> int:
        """
        The number of characters to use for context stuffing.

        This is a cost-benefit decision rather than an inherent model limit.
        """
        return 0

    def generate(self, prompt: ChatThread) -> ChatStream:
        """
        Generates a response to a prompt.

        Args:
            prompt: The chat thread to respond to.

        Returns:
            A `ChatStream` of response chunks.
        """
        raise NotImplementedError

__all__ = [
    'Model',
]
