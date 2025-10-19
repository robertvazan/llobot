"""
Prompt message environment component.
"""
from __future__ import annotations

class PromptEnv:
    """
    An environment component that holds the current prompt message.
    """
    _prompt: str = ''

    def set(self, prompt: str):
        """
        Sets the current prompt message.

        Args:
            prompt: The prompt message content.
        """
        self._prompt = prompt

    def get(self) -> str:
        """
        Gets the current prompt message.

        Returns:
            The prompt message content, or an empty string if not set.
        """
        return self._prompt

__all__ = [
    'PromptEnv',
]
