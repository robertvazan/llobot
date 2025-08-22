from __future__ import annotations
from functools import cache
from llobot.roles.editor import Editor
from llobot.prompts import SystemPrompt, Prompt
import llobot.prompts

@cache
def system() -> SystemPrompt:
    """
    Returns the standard system prompt for the coder role.
    """
    return SystemPrompt(
        llobot.prompts.read('coder.md'),
        llobot.prompts.coding(),
        llobot.prompts.documentation(),
        llobot.prompts.answering(),
    )

class Coder(Editor):
    """
    A role specialized for software development tasks.
    """
    def __init__(self, name: str, *, prompt: str | Prompt = system(), **kwargs):
        """
        Creates a new coder role.

        :param prompt: The system prompt to use. Standard coder prompt is used by default.
        :param kwargs: Additional arguments for the underlying editor role.
        """
        super().__init__(name, prompt=prompt, **kwargs)

__all__ = [
    'system',
    'Coder',
]
