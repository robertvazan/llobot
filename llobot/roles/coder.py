from __future__ import annotations
from functools import cache
from llobot.roles.editor import Editor
from llobot.instructions import SystemPrompt
import llobot.instructions

@cache
def system() -> SystemPrompt:
    """
    Returns the standard system prompt for the coder role.
    """
    return llobot.instructions.prepare(
        llobot.instructions.read('coder.md'),
        *llobot.instructions.coding(),
        *llobot.instructions.answering(),
    )

class Coder(Editor):
    """
    A role specialized for software development tasks.
    """
    def __init__(self, *, instructions: str = system().compile(), **kwargs):
        """
        Creates a new coder role.

        :param instructions: The system prompt to use. Standard coder prompt is used by default.
        :param kwargs: Additional arguments for the underlying editor role.
        """
        super().__init__(instructions=instructions, **kwargs)

__all__ = [
    'system',
    'Coder',
]

