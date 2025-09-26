"""
Crammers for selecting few-shot examples.
"""
from __future__ import annotations
from functools import cache
from typing import Iterable
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder

class ExampleCrammer:
    """
    Base class for crammers that select few-shot examples.

    An example crammer's goal is to select a subset of provided examples
    that fit within the budget of a `ChatBuilder`.
    """
    def cram(self, builder: ChatBuilder, examples: Iterable[ChatBranch]) -> list[ChatBranch]:
        """
        Selects examples and adds them to the builder.

        Args:
            builder: The chat builder to add examples to.
            examples: An iterable of candidate examples.

        Returns:
            A list of the examples that were successfully added to the builder.
        """
        raise NotImplementedError

@cache
def standard_example_crammer() -> ExampleCrammer:
    """
    Returns the standard example crammer.
    """
    from llobot.crammers.example.greedy import GreedyExampleCrammer
    return GreedyExampleCrammer()

__all__ = [
    'ExampleCrammer',
    'standard_example_crammer',
]
