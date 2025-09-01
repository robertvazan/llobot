from __future__ import annotations
from functools import cache
import re
from llobot.chats import ChatIntent, ChatBuilder, ChatBranch, ChatMessage
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

@cache
def plain(affirmation: str = 'Okay.') -> PromptFormatter:
    def render(prompt: str) -> ChatBranch:
        if not prompt:
            return ChatBranch()
        chat = ChatBuilder()
        chat.add(ChatMessage(ChatIntent.SYSTEM, prompt))
        chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
        return chat.build()
    return create(render)

@cache
def reminder(
    pattern: str = r'^- IMPORTANT:\s*(.+)$',
    header: str = 'Reminder:',
    affirmation: str = 'Okay.'
) -> PromptFormatter:
    def render(prompt: str) -> ChatBranch:
        matches = re.findall(pattern, prompt, re.MULTILINE)
        if not matches:
            return ChatBranch()

        lines = []
        if header:
            lines.append(header)
            lines.append('')

        for match in matches:
            lines.append(f'- {match}')

        content = '\n'.join(lines)
        chat = ChatBuilder()
        chat.add(ChatMessage(ChatIntent.SYSTEM, content))
        chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
        return chat.build()

    return create(render)

@cache
def standard() -> PromptFormatter:
    return plain()

__all__ = [
    'PromptFormatter',
    'create',
    'plain',
    'reminder',
    'standard',
]
