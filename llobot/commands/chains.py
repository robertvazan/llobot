"""
Step chain implementation for combining multiple commands and other steps.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.commands import Step

class StepChain:
    """
    A class that processes a sequence of steps in order.

    The chain calls `process` on each of its constituent steps.
    This allows for ordered execution of different command types and other steps.
    """
    _steps: tuple[Step, ...]

    def __init__(self, *steps: Step):
        """
        Creates a new step chain.

        Args:
            *steps: A sequence of steps to process in order.
        """
        self._steps = steps

    def process(self, env: Environment):
        """
        Calls `process` on each step in the chain.

        Args:
            env: The environment to manipulate.
        """
        for step in self._steps:
            step.process(env)

__all__ = [
    'StepChain',
]
