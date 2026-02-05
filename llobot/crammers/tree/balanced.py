from __future__ import annotations
import heapq
from dataclasses import dataclass, field
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

@dataclass(order=True)
class QueueItem:
    cost: int
    path: PurePosixPath = field(compare=False)
    text: str = field(compare=False)
    branching_factor: int = field(compare=False)
    subdirectories: list[PurePosixPath] = field(compare=False)

class BalancedTreeCrammer(TreeCrammer):
    """
    A tree crammer that prioritizes directories based on a cost function.

    It uses a balanced tree exploration strategy. Interesting properties:

    - It deprioritizes deep directories that are part of widely branching
      directory tree.
    - It therefore implicitly gives higher priority to more unique and therefore
      likely more interesting directories.
    - There's only a small penalty for single-member directories common in Java
      projects.
    - It also deprioritizes directories with a lot of items, especially deep in
      the hierarchy.
    - If a directory is included, its parents are also included.
    - While it tries to distribute the budget evenly among peer subdirectories,
      it also naturally recycles unused budget if some subtree is small.
    """
    _budget: int
    _note: str

    def __init__(
        self,
        *,
        budget: int = 50_000,
        note: str = (
            "Project files are listed below. "
            "Some directories might have been omitted for brevity."
        )
    ):
        """
        Creates a new balanced tree crammer.

        Args:
            budget: The character budget for the tree.
            note: A note to display above the file tree.
        """
        self._budget = budget
        self._note = note

    def cram(self, env: Environment) -> None:
        """
        Adds the project tree to the builder, prioritizing important directories.
        """
        project = env[ProjectEnv].union
        prefixes = project.prefixes

        # Priority queue
        queue: list[QueueItem] = []

        # Accepted directories: path -> text
        accepted: dict[PurePosixPath, str] = {}
        used_budget = 0

        def process_directory(
            path: PurePosixPath,
            base_cost: int,
            branching_factor: int
        ) -> QueueItem:
            items = project.items(path)

            # Sort items for consistent rendering
            items.sort(key=lambda i: i.path.name)

            lines = []
            if path != PurePosixPath('.'):
                lines.append(f"~/{path}:")

            subdirs = []
            for item in items:
                name = item.path.name
                if isinstance(item, ProjectDirectory):
                    name += '/'
                    if project.tracked(item):
                        subdirs.append(item.path)
                elif isinstance(item, ProjectLink):
                    name += f' -> {item.target}'
                lines.append(name)

            text = "\n".join(lines) + "\n\n"

            # Cost calculation
            cost = base_cost + len(text) * branching_factor

            return QueueItem(cost, path, text, branching_factor, subdirs)

        # Initialize with prefixes
        for prefix in prefixes:
            # Prefixes are roots, start with 0 base cost and branching factor 1
            item = process_directory(prefix, 0, 1)
            heapq.heappush(queue, item)

        while queue:
            item = heapq.heappop(queue)

            # Check budget
            added_cost = len(item.text)

            if used_budget + added_cost > self._budget:
                break

            accepted[item.path] = item.text
            used_budget += added_cost

            # Add subdirectories
            num_subdirs = len(item.subdirectories)
            next_bf = item.branching_factor * num_subdirs

            for sub_path in item.subdirectories:
                if sub_path in prefixes:
                    continue

                child_item = process_directory(sub_path, item.cost, next_bf)
                heapq.heappush(queue, child_item)

        if not accepted:
            return

        # Sort accepted lexicographically
        sorted_paths = sorted(accepted.keys())

        full_text = "".join(accepted[path] for path in sorted_paths).strip()

        message = ChatMessage(
            ChatIntent.SYSTEM,
            markdown_code_details(
                "Project files", "", full_text, header=self._note
            )
        )
        env[ContextEnv].builder.add(ChatThread([message]))

__all__ = [
    'BalancedTreeCrammer',
]
