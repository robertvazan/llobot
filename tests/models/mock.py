"""
A mock model for testing.
"""
from __future__ import annotations
from typing import Iterable
from llobot.models import Model
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import ChatStream
from llobot.utils.values import ValueTypeMixin

class MockModel(Model, ValueTypeMixin):
    """
    A model that records prompts and returns a canned response.
    """
    _name: str
    _response: str
    _history: list[ChatThread]

    def __init__(self, name: str, *,
        response: str = "Mock response",
    ):
        """
        Initializes the mock model.

        Args:
            name: The name for this model instance.
            response: The response to return from generate().
        """
        self._name = name
        self._response = response
        self._history = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return f'mock/{self._name}'

    @property
    def history(self) -> tuple[ChatThread, ...]:
        """Returns the list of prompts received by generate()."""
        return tuple(self._history)

    def generate(self, prompt: ChatThread) -> ChatStream:
        """
        Records the prompt and yields the configured response.

        Args:
            prompt: The chat thread to respond to.

        Returns:
            A `ChatStream` containing the canned response.
        """
        self._history.append(prompt)
        yield ChatIntent.RESPONSE
        yield self._response

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_history']

__all__ = [
    'MockModel',
]
