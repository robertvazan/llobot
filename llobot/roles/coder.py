from __future__ import annotations
from functools import cache
from llobot.roles.editor import Editor
from llobot.prompts import (
    SystemPrompt,
    Prompt,
    read_prompt,
    answering_prompt_section,
    coding_prompt_section,
    documentation_prompt_section,
)
from llobot.models import Model

@cache
def coder_system_prompt() -> SystemPrompt:
    """
    Returns the standard system prompt for the coder role.
    """
    return SystemPrompt(
        read_prompt('coder.md'),
        answering_prompt_section(),
        coding_prompt_section(),
        documentation_prompt_section(),
    )

class Coder(Editor):
    """
    A role specialized for software development tasks.
    """
    def __init__(self, name: str, model: Model, *, prompt: str | Prompt = coder_system_prompt(), **kwargs):
        """
        Creates a new coder role.

        :param prompt: The system prompt to use. Standard coder prompt is used by default.
        :param kwargs: Additional arguments for the underlying editor role.
        """
        super().__init__(name, model, prompt=prompt, **kwargs)

__all__ = [
    'coder_system_prompt',
    'Coder',
]
