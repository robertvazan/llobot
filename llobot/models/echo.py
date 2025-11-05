"""
An echo model for testing and debugging.
"""
from __future__ import annotations
from llobot.models import Model
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import ChatStream
from llobot.formats.monolithic import MonolithicFormat, standard_monolithic_format
from llobot.utils.values import ValueTypeMixin

class EchoModel(Model, ValueTypeMixin):
    """
    A model that simply echoes back the monolithic content of the prompt.
    """
    _name: str
    _context_budget: int
    _format: MonolithicFormat

    def __init__(self, name: str, *,
        context_budget: int = 100_000,
        format: MonolithicFormat | None = None,
    ):
        """
        Initializes the echo model.

        Args:
            name: The name for this model instance.
            context_budget: The context budget to report.
            format: The format to use for rendering the prompt.
                    Defaults to the standard monolithic format.
        """
        self._name = name
        self._context_budget = context_budget
        self._format = format if format is not None else standard_monolithic_format()

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatThread) -> ChatStream:
        """
        Generates a response by returning the prompt's content as a stream.

        Args:
            prompt: The chat thread to echo.

        Returns:
            A `ChatStream` containing the monolithic prompt content.
        """
        content = self._format.render(prompt)
        if content:
            yield ChatIntent.RESPONSE
            yield content

__all__ = [
    'EchoModel',
]
