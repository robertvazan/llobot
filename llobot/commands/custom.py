"""
Custom step for executing arbitrary callables.
"""
from __future__ import annotations
from typing import Callable
from llobot.environments import Environment
from llobot.commands import Step

class CustomStep(Step):
    """
    A step that executes a custom function on the environment.
    """
    _action: Callable[[Environment], None]

    def __init__(self, action: Callable[[Environment], None]):
        """
        Initializes the custom step with a given action.

        Args:
            action: A callable that takes an Environment and returns None.
        """
        self._action = action

    def process(self, env: Environment):
        """
        Executes the custom action.

        Args:
            env: The environment to pass to the action.
        """
        self._action(env)

__all__ = [
    'CustomStep',
]
