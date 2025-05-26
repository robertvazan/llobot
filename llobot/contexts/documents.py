from __future__ import annotations
from pathlib import Path
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.scores.knowledge import KnowledgeScores
from llobot.contexts import Context, ContextChunk
import llobot.scores.knowledge
import llobot.contexts

# Contains exactly one document and nothing else.
class DocumentChunk(ContextChunk):
    @property
    def path(self) -> Path:
        raise NotImplementedError

    @property
    def content(self) -> str:
        raise NotImplementedError

    @property
    def knowledge(self) -> Knowledge:
        return Knowledge({self.path: self.content})

    @property
    def knowledge_cost(self) -> KnowledgeScores:
        return KnowledgeScores({self.path: self.cost})

class _AnnotatedDocumentChunk(DocumentChunk):
    _chat: ChatBranch
    _cost: int
    _path: Path
    _content: str

    def __init__(self, chat: ChatBranch, path: Path, content: str):
        self._chat = chat
        self._cost = chat.cost
        self._path = path
        self._content = content

    @property
    def chat(self) -> ChatBranch:
        return self._chat

    @property
    def cost(self) -> int:
        return self._cost

    @property
    def path(self) -> Path:
        return self._path

    @property
    def content(self) -> str:
        return self._content

def annotate(chat: ChatBranch, path: Path, content: str) -> Context:
    return _AnnotatedDocumentChunk(chat, path, content) if chat and content else llobot.contexts.empty()

def bulk(chat: ChatBranch, knowledge: Knowledge, cost: KnowledgeScores | None = None) -> Context:
    if cost is None:
        cost = llobot.scores.knowledge.normalize(llobot.scores.knowledge.length(knowledge), chat.cost)
    class BulkDocumentChunk(ContextChunk):
        @property
        def chat(self) -> ChatBranch:
            return chat
        @property
        def knowledge(self) -> Knowledge:
            return knowledge
        @property
        def knowledge_cost(self) -> KnowledgeScores:
            return cost
    return BulkDocumentChunk()

__all__ = [
    'DocumentChunk',
    'annotate',
    'bulk',
]

