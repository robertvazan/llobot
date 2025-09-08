"""
Execution environments for roles.

This package provides the `Environment` class, which serves as a container
for stateful components that roles can use to execute commands included in user's
request.

Submodules
----------
projects
    Selected project.
knowledge
    Knowledge base for selected project.
retrievals
    Document retrievals.
session
    Session messages.
replay
    Replay controls.
cutoff
    Knowledge cutoff timestamp.
commands
    Unprocessed command queue.
context
    LLM context accumulator.
"""
from __future__ import annotations
from typing import Any, Type, TypeVar

class Environment:
    """
    A container for stateful components that are lazily instantiated.

    The environment holds at most one instance of each component class.
    """
    _components: dict[Type[Any], Any]

    def __init__(self):
        self._components = {}

    def __getitem__(self, cls: Type['T']) -> 'T':
        """
        Gets or creates a component of the given class.

        If a component of the requested class already exists in the environment,
        it is returned. Otherwise, a new instance is created and stored for
        future requests.

        Args:
            cls: The class of the component to retrieve.

        Returns:
            The component instance.
        """
        if cls not in self._components:
            self._components[cls] = cls()
        return self._components[cls]

T = TypeVar('T')

__all__ = [
    'Environment',
]
