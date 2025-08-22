from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder, ChatBranch
from llobot.prompts import Prompt

class PromptFormatter:
    def render(self, prompt: str) -> ChatBranch:
        return ChatBranch()

    def __call__(self, prompt: str | Prompt) -> ChatBranch:
        return self.render(str(prompt))

def create(function: Callable[[str], ChatBranch]) -> PromptFormatter:
    class LambdaPromptFormatter(PromptFormatter):
        def render(self, prompt: str) -> ChatBranch:
            return function(prompt)
    return LambdaPromptFormatter()

@lru_cache
def standard(affirmation: str = 'Okay.') -> PromptFormatter:
    def render(prompt: str) -> ChatBranch:
        if not prompt:
            return ChatBranch()
        chat = ChatBuilder()
        chat.add(ChatIntent.SYSTEM)
        chat.add(prompt)
        chat.add(ChatIntent.AFFIRMATION)
        chat.add(affirmation)
        return chat.build()
    return create(render)

__all__ = [
    'PromptFormatter',
    'create',
    'standard',
]
