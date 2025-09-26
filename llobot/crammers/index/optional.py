from __future__ import annotations
from llobot.chats.builders import ChatBuilder
from llobot.crammers.index import IndexCrammer
from llobot.formats.indexes import IndexFormat, standard_index_format
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.utils.values import ValueTypeMixin

class OptionalIndexCrammer(IndexCrammer, ValueTypeMixin):
    """
    An index crammer that includes the full index or nothing.

    This crammer formats the entire index using the specified
    index format. If the formatted index fits within the budget, it is added
    to the builder. Otherwise, nothing is added.
    """
    _index_format: IndexFormat

    def __init__(self, *, index_format: IndexFormat = standard_index_format()):
        """
        Creates a new optional index crammer.

        Args:
            index_format: Formatter to use for rendering the index.
        """
        self._index_format = index_format

    def cram(self, builder: ChatBuilder, knowledge: Knowledge) -> KnowledgeIndex:
        """
        Adds the full knowledge index to the builder if it fits.
        """
        if not knowledge:
            return KnowledgeIndex()

        # Format index
        index_chat = self._index_format.render_chat(knowledge)
        if not index_chat:
            return KnowledgeIndex()

        builder.mark()
        builder.add(index_chat)

        if builder.unused < 0:
            builder.undo()
            return KnowledgeIndex()
        return knowledge.keys()

__all__ = [
    'OptionalIndexCrammer',
]
