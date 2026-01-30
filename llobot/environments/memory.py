"""
Memory environment component.
"""
from __future__ import annotations
from llobot.memories.examples import ExampleMemory

class MemoryEnv:
    """
    An environment component that holds the example memory.
    """
    _examples: ExampleMemory | None

    def __init__(self):
        self._examples = None

    def configure(self, examples: ExampleMemory):
        """
        Configures the example memory to use.
        """
        self._examples = examples

    @property
    def examples(self) -> ExampleMemory:
        """
        Gets the configured example memory.

        Raises:
            ValueError: If the example memory has not been configured.
        """
        if self._examples is None:
            raise ValueError("Example memory is not configured for this role.")
        return self._examples

__all__ = [
    'MemoryEnv',
]
