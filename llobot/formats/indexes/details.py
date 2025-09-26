"""
Index format that wraps output in HTML details/summary tags.
"""
from __future__ import annotations
from llobot.formats.indexes import IndexFormat
from llobot.knowledge import Knowledge
from llobot.utils.text import markdown_code_details
from llobot.utils.values import ValueTypeMixin

class DetailsIndexFormat(IndexFormat, ValueTypeMixin):
    """
    An index format that wraps the output of another format in a
    collapsible details/summary section.
    """
    _title: str
    _inner: IndexFormat

    def __init__(self, inner: IndexFormat, *, title: str = 'Project files'):
        """
        Creates a new details index format.

        Args:
            inner: The inner format to wrap.
            title: Title to use for the details/summary section.
        """
        self._inner = inner
        self._title = title

    def render(self, knowledge: Knowledge) -> str:
        """
        Renders the index using the inner format and wraps it.

        Args:
            knowledge: The knowledge to render.

        Returns:
            A Markdown string with the rendered index inside details/summary.
        """
        content = self._inner.render(knowledge)
        if not content:
            return ''
        return markdown_code_details(self._title, '', content)

__all__ = [
    'DetailsIndexFormat',
]
