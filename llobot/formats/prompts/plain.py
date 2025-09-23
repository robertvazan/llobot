"""
Plain prompt format.
"""
from __future__ import annotations
from llobot.prompts import Prompt
from llobot.formats.prompts import PromptFormat
from llobot.utils.values import ValueTypeMixin

class PlainPromptFormat(PromptFormat, ValueTypeMixin):
    """
    A prompt format that renders the prompt as a simple string.
    """
    def render(self, prompt: str | Prompt) -> str:
        """
        Renders the prompt by converting it to a string.

        Args:
            prompt: The prompt to render.

        Returns:
            The string representation of the prompt.
        """
        return str(prompt)

__all__ = [
    'PlainPromptFormat',
]
