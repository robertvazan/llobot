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
sessions
    Session messages.
cutoffs
    Knowledge cutoff timestamp.
"""
from __future__ import annotations
import weakref
from typing import Type, TypeVar

class Environment:
    """
    A container for stateful components that are lazily instantiated.

    The environment holds at most one instance of each component class.
    Components must be subclasses of `EnvBase`.
    """
    _components: dict[Type[EnvBase], EnvBase]

    def __init__(self):
        self._components = {}

    def __getitem__(self, cls: Type[T]) -> T:
        """
        Gets or creates a component of the given class.

        If a component of the requested class already exists in the environment,
        it is returned. Otherwise, a new instance is created, attached to this
        environment, and stored for future requests.

        Args:
            cls: The class of the component to retrieve. Must be a subclass of `EnvBase`.

        Returns:
            The component instance.

        Raises:
            TypeError: If `cls` is not a subclass of `EnvBase`.
        """
        if not issubclass(cls, EnvBase):
            raise TypeError("Can only store subclasses of EnvBase.")

        if cls not in self._components:
            component = cls()
            component.attach(self)
            self._components[cls] = component

        # The component is guaranteed to be of type T because we checked it's not in the dict,
        # created it with cls(), and stored it.
        return self._components[cls]

class EnvBase:
    """
    Base class for components that can be stored in an `Environment`.

    Subclasses have access to their containing environment via the `env` property.
    """
    _env_ref: weakref.ReferenceType[Environment] | None = None

    def attach(self, env: Environment):
        """
        Attaches this component to an environment.

        This method is called by the `Environment` when the component is created.
        It should not be called directly.

        Args:
            env: The environment to attach to.
        """
        self._env_ref = weakref.ref(env)

    @property
    def env(self) -> Environment:
        """
        The environment this component is part of.

        Returns:
            The `Environment` instance.

        Raises:
            RuntimeError: If the component is not attached to an environment,
                          or if the environment has been destroyed.
        """
        if self._env_ref is None:
            raise RuntimeError("Component is not attached to an environment.")
        env = self._env_ref()
        if env is None:
            raise RuntimeError("Environment has been destroyed.")
        return env

T = TypeVar('T', bound=EnvBase)

__all__ = [
    'Environment',
    'EnvBase',
]
