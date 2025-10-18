"""
An echo model for testing and debugging.
"""
from __future__ import annotations
from llobot.models import Model
from llobot.chats.thread import ChatThread
from llobot.chats.monolithic import monolithic_chat
from llobot.models.streams import ModelStream, text_stream
from llobot.utils.values import ValueTypeMixin

class EchoModel(Model, ValueTypeMixin):
    """
    A model that simply echoes back the monolithic content of the prompt.
    """
    _name: str
    _context_budget: int

    def __init__(self, name: str, *, context_budget: int = 100_000):
        """
        Initializes the echo model.

        Args:
            name: The name for this model instance.
            context_budget: The context budget to report.
        """
        self._name = name
        self._context_budget = context_budget

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatThread) -> ModelStream:
        """
        Generates a response by returning the prompt's content as a stream.

        Args:
            prompt: The chat thread to echo.

        Returns:
            A `ModelStream` containing the monolithic prompt content.
        """
        return text_stream(monolithic_chat(prompt))

__all__ = [
    'EchoModel',
]
