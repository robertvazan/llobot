"""
Prompt message environment component.
"""
from __future__ import annotations

class PromptEnv:
    """
    An environment component that holds the current prompt message.
    It also tracks whether this is the last prompt in the chat.
    """
    _prompt: str = ''
    _is_last: bool = False

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

    def mark_last(self):
        """
        Marks the current prompt as the last one in the chat.
        """
        self._is_last = True

    @property
    def is_last(self) -> bool:
        """
        Checks whether the current prompt is the last one in the chat.
        """
        return self._is_last

__all__ = [
    'PromptEnv',
]
