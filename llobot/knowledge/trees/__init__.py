"""
Hierarchical directory tree representation of knowledge.

This package defines `KnowledgeTree` for representing directory structures. It
provides functions for creating trees from various knowledge representations and
for converting them back into rankings.

Submodules
----------
builder
    `KnowledgeTreeBuilder` for incremental construction of trees.
ranked
    `ranked_tree` function for building a tree from a `KnowledgeRanking`.
lexicographical
    `lexicographical_tree` function for building a lexicographically sorted tree.
overviews
    `overviews_first_tree` for building a tree with overview files prioritized.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
from llobot.utils.values import ValueTypeMixin
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking, coerce_ranking
from llobot.knowledge.subsets import KnowledgeSubset

class KnowledgeTree(ValueTypeMixin):
    """
    Represents a hierarchical directory tree structure containing files and subdirectories.

    The tree is defined by a base path, a list of files in that directory, and a list of subtrees
    representing subdirectories. This structure preserves the original order of files and directories.
    It is a value-like object.
    """
    _base: Path
    _files: tuple[str, ...]
    _subtrees: tuple[KnowledgeTree, ...]
    _subtrees_by_name: dict[str, KnowledgeTree]

    def __init__(self, base: Path | str = '.', files: list[str] = [], subtrees: list[KnowledgeTree] = []):
        """
        Creates a new knowledge tree.

        Args:
            base: Base path for this tree node. Must be relative.
            files: List of file names in this directory.
            subtrees: List of subtrees representing subdirectories.

        Raises:
            ValueError: If base path is absolute, if there are name conflicts between files
                       and subtrees, or if subtree base paths are not one level below parent.
        """
        self._base = Path(base)
        self._files = tuple(files)
        self._subtrees = tuple(subtrees)

        # Check that base path is relative
        if self._base.is_absolute():
            raise ValueError(f"Base path must be relative: {self._base}")

        # Check for name conflicts
        names = set(self._files) | set(subtree.base.name for subtree in self._subtrees)
        if len(names) != len(self._files) + len(self._subtrees):
            raise ValueError("Directory entry name conflict")

        # Check that subtrees have base path one level below parent
        for subtree in self._subtrees:
            if subtree.base.parent != self._base:
                raise ValueError(f"Subtree base {subtree.base} is not one level below parent base {self._base}")

        # Build subtrees lookup dict
        self._subtrees_by_name = {subtree.base.name: subtree for subtree in self._subtrees}

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_subtrees_by_name']

    @property
    def base(self) -> Path:
        """The base path of this tree node."""
        return self._base

    @property
    def files(self) -> list[str]:
        """List of file names in this directory."""
        return list(self._files)

    @property
    def subtrees(self) -> list[KnowledgeTree]:
        """List of subtrees representing subdirectories."""
        return list(self._subtrees)

    def __bool__(self) -> bool:
        """Returns True if the tree contains any files or subtrees."""
        return bool(self._files or self._subtrees)

    @property
    def directories(self) -> list[str]:
        """Names of direct subdirectories in this tree node."""
        return [subtree.base.name for subtree in self._subtrees]

    @property
    def file_paths(self) -> list[Path]:
        """Full paths of all files in this directory (base path plus file name)."""
        return [self._base / filename for filename in self._files]

    @property
    def directory_paths(self) -> list[Path]:
        """Full paths of all direct subdirectories."""
        return [self._base / subtree.base.name for subtree in self._subtrees]

    def __getitem__(self, path: Path | str) -> KnowledgeTree:
        """
        Returns the descendant tree node with the given base path, or an empty tree if not found.

        Args:
            path: Path to look up in the tree.

        Returns:
            The matching subtree or an empty tree if no match is found.

        Raises:
            ValueError: If the path is outside this tree.
        """
        path = Path(path)

        # If path matches our base, return self
        if path == self._base:
            return self

        # Check that the path is relative to our base
        if not path.is_relative_to(self._base):
            raise ValueError(f'Path is outside the tree: {path}')

        relative = path.relative_to(self._base)
        assert relative.parts, "Relative path should have parts if it's different from base"

        # Look for subtree matching first part of relative path
        first_part = relative.parts[0]
        subtree = self._subtrees_by_name.get(first_part)
        if not subtree:
            return KnowledgeTree(path)

        # Recursively search in subtree
        return subtree[path]

    @property
    def all_trees(self) -> list[KnowledgeTree]:
        """All subtrees in depth-first prefix order, starting with self."""
        result = [self]
        for subtree in self._subtrees:
            result.extend(subtree.all_trees)
        return result

    @property
    def all_paths(self) -> list[Path]:
        """All file paths in the tree, visiting tree's files before its subtrees."""
        result = []
        for tree in self.all_trees:
            result.extend(tree.file_paths)
        return result

KnowledgeTreePrecursor = KnowledgeTree | KnowledgeRanking | KnowledgeIndex | Knowledge

def standard_tree(index: KnowledgeTreePrecursor) -> KnowledgeTree:
    """
    Creates the standard knowledge tree.

    The standard tree has overview files listed before their siblings.
    """
    from llobot.knowledge.trees.overviews import overviews_first_tree
    return overviews_first_tree(index)

def coerce_tree(material: KnowledgeTreePrecursor) -> KnowledgeTree:
    """
    Converts various knowledge structures to a KnowledgeTree.

    If the material is not already a `KnowledgeTree`, it will be converted
    to a pre-order lexicographically sorted ranking and then into a tree.

    Args:
        material: The structure to convert. Can be a tree, ranking, index, or knowledge.

    Returns:
        A KnowledgeTree representation of the input material.
    """
    if isinstance(material, KnowledgeTree):
        return material
    # Local import to avoid circular dependency
    from llobot.knowledge.trees.ranked import ranked_tree
    ranking = coerce_ranking(material)
    return ranked_tree(ranking)

__all__ = [
    'KnowledgeTreePrecursor',
    'KnowledgeTree',
    'standard_tree',
    'coerce_tree',
]
