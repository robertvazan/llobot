from __future__ import annotations
from functools import cache
import re
from llobot.chats.intents import ChatIntent
from llobot.chats.builders import ChatBuilder
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.prompts import Prompt

class PromptFormatter:
    def render(self, prompt: str) -> ChatBranch:
        return ChatBranch()

    def __call__(self, prompt: str | Prompt) -> ChatBranch:
        return self.render(str(prompt))

def create_prompt_formatter(function: Callable[[str], ChatBranch]) -> PromptFormatter:
    class LambdaPromptFormatter(PromptFormatter):
        def render(self, prompt: str) -> ChatBranch:
            return function(prompt)
    return LambdaPromptFormatter()

@cache
def plain_prompt_formatter(affirmation: str = 'Okay.') -> PromptFormatter:
    def render(prompt: str) -> ChatBranch:
        if not prompt:
            return ChatBranch()
        chat = ChatBuilder()
        chat.add(ChatMessage(ChatIntent.SYSTEM, prompt))
        chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
        return chat.build()
    return create_prompt_formatter(render)

@cache
def reminder_prompt_formatter(
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

    return create_prompt_formatter(render)

@cache
def standard_prompt_formatter() -> PromptFormatter:
    return plain_prompt_formatter()

__all__ = [
    'PromptFormatter',
    'create_prompt_formatter',
    'plain_prompt_formatter',
    'reminder_prompt_formatter',
    'standard_prompt_formatter',
]
