"""
Components for stuffing information into the context.

This package provides "crammers," which are responsible for selecting and formatting
information (such as system prompts, examples, knowledge documents, or file indexes)
to fit within a given context size budget for an LLM prompt.

Base Interface
--------------
Crammer
    Base interface for all crammers with a single `cram(env)` method.

Specific Crammers
-----------------
CrammerChain
    A sequence of crammers executed in order.
ExampleCrammer
    Selects a set of recent examples that fit within a budget.
DateCrammer
    Adds current date to the context.
TreeCrammer
    Formats file trees, deciding whether to include them based on budget.
KnowledgeCrammer
    Selects a subset of knowledge documents based on scores and budget.
"""
from __future__ import annotations
from types import NotImplementedType
from llobot.environments import Environment
from llobot.utils.values import ValueTypeMixin

class Crammer(ValueTypeMixin):
    """
    Base interface for components that stuff information into the context.

    Crammers are responsible for adding content to the `ContextEnv` within the provided
    `Environment`. They manage their own budget and use the environment's `ChatBuilder`
    to track usage and enforce limits on their own output.
    """
    def cram(self, env: Environment) -> None:
        """
        Adds content to the context in the provided environment.

        Args:
            env: The environment containing context builder and other resources.
        """
        raise NotImplementedError

    def __add__(self, other: object) -> Crammer | NotImplementedType:
        """
        Combines this crammer with another one into a chain.
        """
        if not isinstance(other, Crammer):
            return NotImplemented
        from llobot.crammers.chain import CrammerChain
        return CrammerChain(self, other)

__all__ = [
    'Crammer',
]
