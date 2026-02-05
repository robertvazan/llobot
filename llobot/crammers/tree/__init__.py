"""
Crammers for formatting and including file trees.

Submodules
----------
balanced
    `BalancedTreeCrammer` that prioritizes directories based on budget.
full
    `FullTreeCrammer` that includes the entire tree.
optional
    `OptionalTreeCrammer` that includes the full tree or nothing.
"""
from __future__ import annotations
from functools import cache
from llobot.crammers import Crammer
from llobot.environments import Environment

class TreeCrammer(Crammer):
    """
    Base class for crammers that format and add file trees to the context.

    A tree crammer decides whether to include a file tree in the prompt
    based on the available budget in the environment.
    """

    def cram(self, env: Environment) -> None:
        """
        Adds a file tree to the builder if it fits the budget.

        Args:
            env: The environment containing context and project.
        """
        raise NotImplementedError

@cache
def standard_tree_crammer() -> TreeCrammer:
    """
    Returns the standard tree crammer.
    """
    from llobot.crammers.tree.balanced import BalancedTreeCrammer
    return BalancedTreeCrammer()

__all__ = [
    'TreeCrammer',
    'standard_tree_crammer',
]
