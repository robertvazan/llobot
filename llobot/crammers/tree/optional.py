from __future__ import annotations
from llobot.crammers.tree import TreeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.indexes import IndexFormat, standard_index_format
from llobot.utils.values import ValueTypeMixin

class OptionalTreeCrammer(TreeCrammer, ValueTypeMixin):
    """
    A tree crammer that includes the full tree or nothing.

    This crammer formats the entire tree using the specified
    index format. If the formatted tree fits within the budget, it is added
    to the builder. Otherwise, nothing is added.
    """
    _index_format: IndexFormat
    _budget: int

    def __init__(self, *, index_format: IndexFormat = standard_index_format(), budget: int = 50_000):
        """
        Creates a new optional tree crammer.

        Args:
            index_format: Formatter to use for rendering the tree.
            budget: The character budget for context stuffing.
        """
        self._index_format = index_format
        self._budget = budget

    def cram(self, env: Environment) -> None:
        """
        Adds the full project tree to the builder if it fits.
        """
        builder = env[ContextEnv].builder
        builder.budget = builder.cost + self._budget

        knowledge = env[ProjectEnv].union.read_all()

        if not knowledge:
            return

        # Format tree
        tree_chat = self._index_format.render_chat(knowledge)
        if not tree_chat:
            return

        builder.mark()
        builder.add(tree_chat)

        if builder.unused < 0:
            builder.undo()
            return

__all__ = [
    'OptionalTreeCrammer',
]
