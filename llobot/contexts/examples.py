from __future__ import annotations
from llobot.chats import ChatBranch, ChatIntent
from llobot.knowledge import Knowledge
from llobot.contexts import Context, ContextChunk
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.contexts
import llobot.formatters.envelopes

# Contains exactly one example and nothing else.
# There is no padding around the example. Chunk's chat is just the example.
class ExampleChunk(ContextChunk):
    @property
    def examples(self) -> list[ChatBranch]:
        return [self.chat]

class _AnnotatedExampleChunk(ExampleChunk):
    _chat: ChatBranch
    _knowledge: Knowledge

    def __init__(self, chat: ChatBranch, knowledge: Knowledge = Knowledge()):
        self._chat = chat
        self._knowledge = knowledge

    @property
    def chat(self) -> ChatBranch:
        return self._chat

    @property
    def knowledge(self) -> Knowledge:
        return self._knowledge

def annotate(*examples: ChatBranch, formatter: EnvelopeFormatter = llobot.formatters.envelopes.standard()) -> Context:
    chunks = []
    for example in examples:
        if not example.is_example():
            raise ValueError('Not an example chat')
        documents = {}
        for message in example:
            if message.intent == ChatIntent.EXAMPLE_RESPONSE:
                for path, content in formatter.parse_all(message.content):
                    documents[path] = content
        chunks.append(_AnnotatedExampleChunk(example, Knowledge(documents)))
    return llobot.contexts.compose(*chunks)

__all__ = [
    'ExampleChunk',
    'annotate',
]

