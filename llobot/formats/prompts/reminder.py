"""
Prompt format that extracts reminders.
"""
from __future__ import annotations
import re
from llobot.prompts import Prompt
from llobot.formats.prompts import PromptFormat
from llobot.utils.values import ValueTypeMixin

class ReminderPromptFormat(PromptFormat, ValueTypeMixin):
    """
    A prompt format that extracts important reminders and formats them.
    """
    _pattern: str
    _header: str

    def __init__(self,
        pattern: str = r'^- IMPORTANT:\s*(.+)$',
        header: str = 'Reminder:',
    ):
        """
        Creates a new reminder prompt format.

        Args:
            pattern: The regex pattern to find reminders.
            header: The header to put above the list of reminders.
        """
        self._pattern = pattern
        self._header = header

    def render(self, prompt: str | Prompt) -> str:
        """
        Renders the prompt by extracting and formatting reminders.

        Args:
            prompt: The prompt to extract reminders from.

        Returns:
            A formatted string of reminders, or an empty string if none are found.
        """
        prompt_str = str(prompt)
        matches = re.findall(self._pattern, prompt_str, re.MULTILINE)
        if not matches:
            return ""

        lines = []
        if self._header:
            lines.append(self._header)
            lines.append('')

        for match in matches:
            lines.append(f'- {match}')

        return '\n'.join(lines)

__all__ = [
    'ReminderPromptFormat',
]
