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

class FullTreeCrammer(TreeCrammer):
    """
    A tree crammer that adds the full project tree to the context.

    This crammer formats the entire tree by walking the project and listing
    all items, including untracked directories (which are listed under their
    parent directory). It ignores the context budget.
    """

    def cram(self, env: Environment) -> None:
        """
        Adds the full project tree to the builder.
        """
        builder = env[ContextEnv].builder
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

        builder.add(ChatThread([message]))

__all__ = [
    'FullTreeCrammer',
]
