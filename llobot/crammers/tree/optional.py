from __future__ import annotations
from llobot.crammers.tree import TreeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv

class OptionalTreeCrammer(TreeCrammer):
    """
    A tree crammer that includes the full tree or nothing.

    This crammer delegates to FullTreeCrammer to format and add the tree.
    If the formatted tree fits within the budget, it is kept.
    Otherwise, the addition is undone.
    """
    _budget: int

    def __init__(self, *, budget: int = 50_000):
        """
        Creates a new optional tree crammer.

        Args:
            budget: The character budget for context stuffing.
        """
        self._budget = budget

    def cram(self, env: Environment) -> None:
        """
        Adds the full project tree to the builder if it fits.
        """
        from llobot.crammers.tree.full import FullTreeCrammer

        builder = env[ContextEnv].builder
        original_budget = builder.budget

        try:
            builder.budget = builder.cost + self._budget
            builder.mark()
            FullTreeCrammer().cram(env)

            if builder.unused < 0:
                builder.undo()
        finally:
            builder.budget = original_budget

__all__ = [
    'OptionalTreeCrammer',
]
