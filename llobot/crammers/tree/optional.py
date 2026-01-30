from __future__ import annotations
from collections import defaultdict
from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.crammers.tree import TreeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.items import ProjectDirectory, ProjectLink
from llobot.utils.text import markdown_code_details
from llobot.utils.values import ValueTypeMixin

class OptionalTreeCrammer(TreeCrammer, ValueTypeMixin):
    """
    A tree crammer that includes the full tree or nothing.

    This crammer formats the entire tree by walking the project and listing
    all items, including untracked directories (which are listed under their
    parent directory). It does not descend into untracked directories, because
    it relies on `Project.walk()`.

    If the formatted tree fits within the budget, it is added to the builder.
    Otherwise, nothing is added.
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
        builder = env[ContextEnv].builder
        builder.budget = builder.cost + self._budget

        project = env[ProjectEnv].union
        groups = defaultdict(list)
        has_items = False

        for item in project.walk():
            has_items = True
            groups[item.path.parent].append(item)

        if not has_items:
            return

        lines = []
        for parent in sorted(groups.keys()):
            if parent == PurePosixPath('.'):
                pass
            else:
                lines.append(f"~/{parent}:")

            for item in groups[parent]:
                name = item.path.name
                if isinstance(item, ProjectDirectory):
                    name += '/'
                elif isinstance(item, ProjectLink):
                    name += f' -> {item.target}'
                lines.append(name)
            lines.append("")

        text = "\n".join(lines).strip()
        message = ChatMessage(ChatIntent.SYSTEM, markdown_code_details("Project files", "", text))

        builder.mark()
        builder.add(ChatThread([message]))

        if builder.unused < 0:
            builder.undo()
            return

__all__ = [
    'OptionalTreeCrammer',
]
