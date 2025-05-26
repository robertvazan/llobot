from __future__ import annotations
from pathlib import Path
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.contexts import Context, ContextChunk
import llobot.knowledge.indexes
import llobot.contexts

# Contains exactly one deletion and nothing else.
class DeletionChunk(ContextChunk):
    @property
    def path(self) -> Path:
        raise NotImplementedError

    @property
    def deletions(self) -> KnowledgeIndex:
        return KnowledgeIndex([self.path])

class _AnnotatedDeletionChunk(DeletionChunk):
    _chat: ChatBranch
    _path: Path

    def __init__(self, chat: ChatBranch, path: Path):
        self._chat = chat
        self._path = path

    @property
    def chat(self) -> ChatBranch:
        return self._chat

    @property
    def path(self) -> Path:
        return self._path

def annotate(chat: ChatBranch, path: Path) -> Context:
    return _AnnotatedDeletionChunk(chat, path) if chat else llobot.contexts.empty()

def bulk(chat: ChatBranch, deletions: KnowledgeIndex | Knowledge) -> Context:
    deletions = llobot.knowledge.indexes.coerce(deletions)
    class BulkDeletionChunk(ContextChunk):
        @property
        def chat(self) -> ChatBranch:
            return chat
        @property
        def deletions(self) -> KnowledgeIndex:
            return deletions
    return BulkDeletionChunk()

__all__ = [
    'DeletionChunk',
    'annotate',
    'bulk',
]

