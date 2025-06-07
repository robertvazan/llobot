from __future__ import annotations
from functools import cache
from llobot.chats import ChatIntent, ChatBranch, ChatBuilder
from llobot.knowledge import Knowledge
from llobot.scores.knowledge import KnowledgeScores
from llobot.knowledge.indexes import KnowledgeIndex

# Context annotates chat or its chunk with structured data.
# Context objects are currently constructed from structured data, but we could also parse information out of model responses in the future.
class Context:
    @property
    def chat(self) -> ChatBranch:
        raise NotImplementedError

    @property
    def cost(self) -> int:
        return self.chat.cost

    @property
    def pretty_cost(self) -> str:
        return self.chat.pretty_cost

    def __bool__(self) -> bool:
        return bool(self.chat)

    # Context hierarchy is flat. If this is a container, it returns children. If this is a child, it returns itself.
    @property
    def chunks(self) -> list[ContextChunk]:
        raise NotImplementedError

    @property
    def knowledge(self) -> Knowledge:
        return Knowledge()

    @property
    def knowledge_cost(self) -> KnowledgeScores:
        return KnowledgeScores()

    @property
    def deletions(self) -> KnowledgeIndex:
        return KnowledgeIndex()

    @property
    def examples(self) -> list[ChatBranch]:
        return []

    def __add__(self, other: Context) -> Context:
        return compose(self, other)

    def __and__(self, other: Context | ChatBranch) -> Context:
        prefix = []
        remaining = other.chat if isinstance(other, Context) else other
        for chunk in self.chunks:
            length = len(chunk.chat)
            if length > len(remaining):
                break
            # Force conversion to list, so that we don't compare chat metadata.
            if list(chunk.chat) != list(remaining[:length]):
                break
            prefix.append(chunk)
            remaining = remaining[length:]
        return compose(*prefix)

    def pretty_structure(self) -> str:
        codes = []
        for chunk in self.chunks:
            if chunk.knowledge:
                codes.append('K')
            elif chunk.deletions:
                codes.append('D')
            elif chunk.examples:
                codes.append('E')
            else:
                codes.append('S')
        s = ''.join(codes)
        return ' '.join(s[i:i+10] for i in range(0, len(s), 10))

class ContextChunk(Context):
    @property
    def chunks(self) -> list[ContextChunk]:
        return [self]

@cache
def empty() -> Context:
    class EmptyContext(Context):
        @property
        def chat(self) -> ChatBranch:
            return ChatBranch()
        @property
        def cost(self) -> int:
            return 0
        @property
        def chunks(self) -> list[ContextChunk]:
            return []
    return EmptyContext()

class _CompositeContext(Context):
    _chunks: list[ContextChunk]
    _chat: ChatBranch
    _cost: int
    _knowledge: Knowledge
    _knowledge_cost: KnowledgeScores
    _deletions: KnowledgeIndex
    _examples: list[ChatBranch]

    def __init__(self, chunks: list[ContextChunk]):
        from llobot.contexts.documents import DocumentChunk
        from llobot.contexts.deletions import DeletionChunk
        from llobot.contexts.examples import ExampleChunk
        chat = ChatBuilder()
        knowledge = {}
        knowledge_cost = {}
        deletions = set()
        examples = []
        for chunk in chunks:
            chat.add(chunk.chat)
            if isinstance(chunk, DocumentChunk):
                knowledge[chunk.path] = chunk.content
                knowledge_cost[chunk.path] = chunk.cost
                deletions.discard(chunk.path)
            elif isinstance(chunk, DeletionChunk):
                deletions.add(chunk.path)
                knowledge.pop(chunk.path, None)
                knowledge_cost.pop(chunk.path, None)
            elif isinstance(chunk, ExampleChunk):
                examples.append(chunk.chat)
                knowledge |= dict(chunk.knowledge)
                knowledge_cost |= dict(chunk.knowledge_cost)
            else:
                knowledge |= dict(chunk.knowledge)
                knowledge_cost |= dict(chunk.knowledge_cost)
                deletions -= set(chunk.knowledge.keys())
                examples.extend(chunk.examples)
        self._chunks = chunks
        self._chat = chat.build()
        self._cost = self._chat.cost
        self._knowledge = Knowledge(knowledge)
        self._knowledge_cost = KnowledgeScores(knowledge_cost)
        self._deletions = KnowledgeIndex(deletions)
        self._examples = examples

    @property
    def chat(self) -> ChatBranch:
        return self._chat

    @property
    def cost(self) -> int:
        return self._cost

    @property
    def chunks(self) -> list[ContextChunk]:
        return self._chunks

    @property
    def knowledge(self) -> Knowledge:
        return self._knowledge

    @property
    def knowledge_cost(self) -> KnowledgeScores:
        return self._knowledge_cost

    @property
    def deletions(self) -> KnowledgeIndex:
        return self._deletions

    @property
    def examples(self) -> list[ChatBranch]:
        return self._examples

def compose(*contexts: Context) -> Context:
    chunks = [chunk for context in contexts for chunk in context.chunks]
    if not chunks:
        return empty()
    if len(chunks) == 1:
        return chunks[0]
    return _CompositeContext(chunks)

class _PlainContext(ContextChunk):
    _chat: ChatBranch
    _cost: int

    def __init__(self, chat: ChatBranch):
        self._chat = chat
        self._cost = chat.cost

    @property
    def chat(self) -> ChatBranch:
        return self._chat

    @property
    def cost(self) -> int:
        return self._cost

def wrap(chat: ChatBranch) -> Context:
    return _PlainContext(chat) if chat else empty()

def system(instructions: str, affirmation: str = 'Okay.') -> Context:
    if not instructions:
        return empty()
    chat = ChatBuilder()
    chat.add(ChatIntent.SYSTEM)
    chat.add(instructions)
    chat.add(ChatIntent.AFFIRMATION)
    chat.add(affirmation)
    return wrap(chat.build())

__all__ = [
    'Context',
    'ContextChunk',
    'empty',
    'compose',
    'wrap',
    'system',
]

