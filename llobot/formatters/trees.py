from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge.trees import KnowledgeTree
import llobot.knowledge.trees
import llobot.text

class TreeFormatter:
    """
    Interface for formatting knowledge trees as Markdown text.

    Tree formatters take a KnowledgeTree and render it as a human-readable Markdown string.
    """

    def render(self, tree: KnowledgeTree) -> str:
        """
        Renders a knowledge tree as Markdown text.

        Args:
            tree: The knowledge tree to render.

        Returns:
            Markdown representation of the tree.
        """
        raise NotImplementedError

    def __call__(self, tree: KnowledgeTree) -> str:
        """Convenience method for calling render()."""
        return self.render(tree)

    def render_sorted(self, material: KnowledgeIndex | Knowledge) -> str:
        """
        Renders knowledge material as a tree after converting and sorting it.

        This method converts the input material to a KnowledgeTree using lexicographical
        ordering and then renders it.

        Args:
            material: Knowledge index or index precursor to render.

        Returns:
            Markdown representation of the sorted tree.
        """
        tree = llobot.knowledge.trees.coerce(material)
        return self.render(tree)

def create(function: Callable[[KnowledgeTree], str]) -> TreeFormatter:
    """
    Creates a tree formatter from a function.

    Args:
        function: Function that takes a KnowledgeTree and returns a Markdown string.

    Returns:
        A TreeFormatter that uses the provided function.
    """
    class LambdaTreeFormatter(TreeFormatter):
        def render(self, tree: KnowledgeTree) -> str:
            return function(tree)
    return LambdaTreeFormatter()

@lru_cache
def flat(title: str) -> TreeFormatter:
    """
    Creates a tree formatter that lists all file paths in a flat list.

    The formatter renders all paths from the tree in a single code block
    within a collapsible details/summary section.

    Args:
        title: Title to use for the details/summary section.

    Returns:
        A TreeFormatter that renders paths as a flat list.
    """
    def render_flat(tree: KnowledgeTree) -> str:
        paths = tree.all_paths
        if not paths:
            return ''
        file_list = '\n'.join(str(path) for path in paths)
        return llobot.text.details(title, '', file_list)
    return create(render_flat)

@lru_cache
def grouped(title: str) -> TreeFormatter:
    """
    Creates a tree formatter that groups files by directory.

    The formatter renders files grouped by their containing directory, with
    directory headers and files listed underneath. Groups are separated by
    empty lines. Root directory files (base path '.') are listed without a header.

    Args:
        title: Title to use for the details/summary section.

    Returns:
        A TreeFormatter that renders paths grouped by directory.
    """
    def render_grouped(tree: KnowledgeTree) -> str:
        sections = []
        for subtree in tree.all_trees:
            if not subtree.files:
                continue

            lines = []

            # Add header unless this is root with base path '.'
            if subtree.base != Path('.'):
                lines.append(f'{subtree.base}:')
                lines.append('')

            # Add files
            for filename in subtree.files:
                lines.append(filename)

            sections.append('\n'.join(lines))

        if not sections:
            return ''

        content = llobot.text.concat(*sections)
        return llobot.text.details(title, '', content)

    return create(render_grouped)

@lru_cache
def standard(title: str = 'Files') -> TreeFormatter:
    """
    Creates the standard tree formatter to be used by default.

    The standard formatter groups files by directory with a default title of 'Files'.

    Args:
        title: Title to use for the details/summary section.

    Returns:
        The standard TreeFormatter (currently grouped formatting).
    """
    return grouped(title)

__all__ = [
    'TreeFormatter',
    'create',
    'flat',
    'grouped',
    'standard',
]
