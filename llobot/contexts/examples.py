from __future__ import annotations
from llobot.chats import ChatBranch
from llobot.contexts import Context, ContextChunk
import llobot.contexts

# Contains exactly one example and nothing else.
# There is no padding around the example. Chunk's chat is just the example.
class ExampleChunk(ContextChunk):
    @property
    def examples(self) -> list[ChatBranch]:
        return [self.chat]

class _AnnotatedExampleChunk(ExampleChunk):
    _chat: ChatBranch

    def __init__(self, chat: ChatBranch):
        self._chat = chat

    @property
    def chat(self) -> ChatBranch:
        return self._chat

def annotate(*examples: ChatBranch) -> Context:
    chunks = []
    for example in examples:
        if not example.is_example():
            raise ValueError('Not an example chat')
        chunks.append(_AnnotatedExampleChunk(example))
    return llobot.contexts.compose(*chunks)

def bulk(chat: ChatBranch, examples: Iterable[ChatBranch]) -> Context:
    examples = list(examples)
    if not chat or not examples:
        return llobot.contexts.empty()
    if any(not example.is_example() for example in examples):
        raise ValueError('Not an example chat')
    class BulkExampleChunk(ContextChunk):
        @property
        def chat(self) -> ChatBranch:
            return chat
        @property
        def examples(self) -> list[ChatBranch]:
            return examples
    return BulkExampleChunk()

__all__ = [
    'ExampleChunk',
    'annotate',
    'bulk',
]

