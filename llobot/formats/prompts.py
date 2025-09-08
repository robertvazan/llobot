from __future__ import annotations
from functools import cache
from typing import Callable
import re
from llobot.chats.intents import ChatIntent
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.prompts import Prompt
from llobot.formats.affirmations import affirmation_turn

class PromptFormat:
    def render(self, prompt: str) -> ChatBranch:
        return ChatBranch()

    def __call__(self, prompt: str | Prompt) -> ChatBranch:
        return self.render(str(prompt))

def create_prompt_format(function: Callable[[str], ChatBranch]) -> PromptFormat:
    class LambdaPromptFormat(PromptFormat):
        def render(self, prompt: str) -> ChatBranch:
            return function(prompt)
    return LambdaPromptFormat()

@cache
def plain_prompt_format() -> PromptFormat:
    def render(prompt: str) -> ChatBranch:
        if not prompt:
            return ChatBranch()
        return affirmation_turn(ChatMessage(ChatIntent.SYSTEM, prompt))
    return create_prompt_format(render)

@cache
def reminder_prompt_format(
    pattern: str = r'^- IMPORTANT:\s*(.+)$',
    header: str = 'Reminder:',
) -> PromptFormat:
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
        return affirmation_turn(ChatMessage(ChatIntent.SYSTEM, content))

    return create_prompt_format(render)

@cache
def standard_prompt_format() -> PromptFormat:
    return plain_prompt_format()

__all__ = [
    'PromptFormat',
    'create_prompt_format',
    'plain_prompt_format',
    'reminder_prompt_format',
    'standard_prompt_format',
]
