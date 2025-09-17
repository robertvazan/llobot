from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.subsets import KnowledgeSubset

class KnowledgeTree:
    """
    Represents a hierarchical directory tree structure containing files and subdirectories.

    The tree is defined by a base path, a list of files in that directory, and a list of subtrees
    representing subdirectories. This structure preserves the original order of files and directories.
    """
    _base: Path
    _files: list[str]
    _subtrees: list[KnowledgeTree]
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
        self._files = list(files)
        self._subtrees = list(subtrees)

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

def ranked_tree(ranking: KnowledgeRanking) -> KnowledgeTree:
    """
    Creates a knowledge tree from a ranking by adding all paths in order.

    Args:
        ranking: A ranking of paths to organize into a tree structure.

    Returns:
        A knowledge tree containing all paths from the ranking.
    """
    builder = KnowledgeTreeBuilder()
    for path in ranking:
        builder.add(path)
    return builder.build()

def lexicographical_tree(index: KnowledgeIndex | KnowledgeRanking | Knowledge) -> KnowledgeTree:
    """
    Creates a knowledge tree from an index or index precursor, sorted lexicographically.

    Args:
        index: Knowledge index or its precursor to convert to a tree.

    Returns:
        A knowledge tree with paths sorted lexicographically.
    """
    from llobot.knowledge.ranking.lexicographical import rank_lexicographically
    ranking = rank_lexicographically(index)
    return ranked_tree(ranking)

def overviews_first_tree(
    index: KnowledgeIndex | KnowledgeRanking | Knowledge,
    *,
    overviews: KnowledgeSubset | None = None
) -> KnowledgeTree:
    """
    Creates a knowledge tree with overview files listed first in each directory.

    Args:
        index: Knowledge index or its precursor to convert to a tree.
        overviews: Subset defining overview files. Defaults to predefined overview subset.

    Returns:
        A knowledge tree with overview files prioritized in each directory.
    """
    # Local import to avoid circular dependency.
    from llobot.knowledge.ranking.lexicographical import rank_lexicographically
    from llobot.knowledge.ranking.overviews import rank_overviews_before_siblings
    initial = rank_lexicographically(index)
    ranking = rank_overviews_before_siblings(initial, overviews=overviews)
    return ranked_tree(ranking)

def standard_tree(index: KnowledgeIndex | KnowledgeRanking | Knowledge) -> KnowledgeTree:
    return overviews_first_tree(index)

def coerce_tree(material: KnowledgeTree | KnowledgeRanking | KnowledgeIndex | Knowledge) -> KnowledgeTree:
    """
    Converts various knowledge structures to a KnowledgeTree.

    Args:
        material: The structure to convert. Can be a tree, ranking, index, or knowledge.

    Returns:
        A KnowledgeTree representation of the input material.
    """
    if isinstance(material, KnowledgeTree):
        return material
    if isinstance(material, KnowledgeRanking):
        return ranked_tree(material)
    # KnowledgeIndex or Knowledge
    return standard_tree(material)

__all__ = [
    'KnowledgeTree',
    'KnowledgeTreeBuilder',
    'ranked_tree',
    'lexicographical_tree',
    'overviews_first_tree',
    'standard_tree',
    'coerce_tree',
]
