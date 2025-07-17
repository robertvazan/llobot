from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatIntent, ChatBuilder, ChatBranch

class InstructionFormatter:
    def render(self, instructions: str) -> ChatBranch:
        return ChatBranch()

    def __call__(self, instructions: str) -> ChatBranch:
        return self.render(instructions)

def create(function: Callable[[str], ChatBranch]) -> InstructionFormatter:
    class LambdaInstructionFormatter(InstructionFormatter):
        def render(self, instructions: str) -> ChatBranch:
            return function(instructions)
    return LambdaInstructionFormatter()

@lru_cache
def standard(affirmation: str = 'Okay.') -> InstructionFormatter:
    def render(instructions: str) -> ChatBranch:
        if not instructions:
            return ChatBranch()
        chat = ChatBuilder()
        chat.add(ChatIntent.SYSTEM)
        chat.add(instructions)
        chat.add(ChatIntent.AFFIRMATION)
        chat.add(affirmation)
        return chat.build()
    return create(render)

__all__ = [
    'InstructionFormatter',
    'create',
    'standard',
]
