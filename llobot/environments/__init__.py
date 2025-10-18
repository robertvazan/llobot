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
cutoff
    Knowledge cutoff timestamp.
commands
    Unprocessed command queue.
context
    LLM context accumulator.
prompt
    Current prompt message.
status
    Status messages.
persistent
    Base class for persistent environment components.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Type, TypeVar
from llobot.environments.persistent import PersistentEnv

class Environment:
    """
    A container for stateful components that are lazily instantiated.
    The environment can be saved to and loaded from a directory on disk.
    """
    _components: dict[Type[Any], Any]
    _load_path: Path | None

    def __init__(self):
        self._components = {}
        self._load_path = None

    def __getitem__(self, cls: Type['T']) -> 'T':
        """
        Gets or creates a component of the given class.

        If a component of the requested class already exists in the environment,
        it is returned. Otherwise, a new instance is created and stored for
        future requests. If a load path is configured and the new component is
        persistent, its state is loaded.

        Args:
            cls: The class of the component to retrieve.

        Returns:
            The component instance.
        """
        if cls not in self._components:
            component = cls()
            self._components[cls] = component
            if self._load_path and isinstance(component, PersistentEnv):
                component.load(self._load_path)
        return self._components[cls]

    def save(self, path: Path):
        """
        Saves all persistent components to the specified directory.

        The directory is created only if there are persistent components to save.

        Args:
            path: The directory to save to.
        """
        persistent_components = [c for c in self._components.values() if isinstance(c, PersistentEnv)]
        if not persistent_components:
            return

        path.mkdir(parents=True, exist_ok=True)

        for component in persistent_components:
            component.save(path)

    def load(self, path: Path):
        """
        Loads all existing persistent components from the specified directory.

        Subsequent lazily-created persistent components will also be loaded from this path.

        Args:
            path: The directory to load from.
        """
        self._load_path = path
        for component in self._components.values():
            if isinstance(component, PersistentEnv):
                component.load(path)

T = TypeVar('T')

__all__ = [
    'Environment',
    'PersistentEnv',
]
