from __future__ import annotations
from functools import cache, lru_cache
from llobot.roles import Role
from llobot.instructions import SystemPrompt
import llobot.roles.editor
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

@lru_cache
def create(*, instructions: str = system().compile(), **kwargs) -> Role:
    """
    Creates a new coder role.

    :param instructions: The system prompt to use. Standard coder prompt is used by default.
    :param kwargs: Additional arguments for the underlying editor role.
    """
    return llobot.roles.editor.create(instructions=instructions, **kwargs)

__all__ = [
    'system',
    'create',
]

