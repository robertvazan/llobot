from __future__ import annotations
from pathlib import Path
from llobot.knowledge.trees import KnowledgeTree

class KnowledgeTreeBuilder:
    """
    A builder for constructing KnowledgeTree instances by adding file paths incrementally.

    The builder automatically creates the necessary directory structure as paths are added,
    maintaining the order in which files and directories are first encountered.
    """
    _base: Path
    _files: list[str]
    _file_names: set[str]
    _subtree_builders: list[KnowledgeTreeBuilder]
    _subtree_names: dict[str, KnowledgeTreeBuilder]

    def __init__(self, base: Path | str = '.'):
        """
        Creates a new tree builder with the given base path.

        Args:
            base: Base path for the root of the tree being built.
        """
        self._base = Path(base)
        self._files = []
        self._file_names = set()
        self._subtree_builders = []
        self._subtree_names = {}

    def add(self, path: Path | str) -> None:
        """
        Adds a file path to the tree, creating nested builders as necessary.

        Args:
            path: Full file path to add to the tree.

        Raises:
            ValueError: If the path is not relative to the base path.
        """
        path = Path(path)

        # If path is not relative to our base, we need to find the right place for it
        if not path.is_relative_to(self._base):
            raise ValueError(f"Path {path} is not relative to base {self._base}")

        relative = path.relative_to(self._base)

        # If this is a direct file in our directory
        if len(relative.parts) == 1:
            filename = relative.name
            if filename not in self._file_names:
                self._files.append(filename)
                self._file_names.add(filename)
        else:
            # This belongs in a subtree
            first_part = relative.parts[0]
            subtree_base = self._base / first_part

            # Get or create subtree builder
            if first_part not in self._subtree_names:
                subtree_builder = KnowledgeTreeBuilder(subtree_base)
                self._subtree_builders.append(subtree_builder)
                self._subtree_names[first_part] = subtree_builder
            else:
                subtree_builder = self._subtree_names[first_part]

            # Add to subtree
            subtree_builder.add(path)

    def build(self) -> KnowledgeTree:
        """Constructs a KnowledgeTree from the current state of the builder."""
        subtrees = [builder.build() for builder in self._subtree_builders]
        return KnowledgeTree(self._base, self._files, subtrees)

__all__ = [
    'KnowledgeTreeBuilder',
]
