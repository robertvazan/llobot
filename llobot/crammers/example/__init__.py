"""
Crammers for selecting few-shot examples.
"""
from __future__ import annotations
from functools import cache
from llobot.environments import Environment

class ExampleCrammer:
    """
    Base class for crammers that select few-shot examples.

    An example crammer's goal is to select a subset of provided examples
    that fit within the budget of the environment's context.
    """
    def cram(self, env: Environment) -> None:
        """
        Selects examples from environment memory and adds them to the context.

        Args:
            env: The environment containing context builder and example memory.
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
