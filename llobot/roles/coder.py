from __future__ import annotations
from functools import cache, lru_cache
from llobot.roles import Role
import llobot.roles.editor
import llobot.instructions

@cache
def description() -> str:
    return llobot.instructions.read('coder.md')

@cache
def instructions() -> str:
    return llobot.instructions.compile(
        description(),
        *llobot.instructions.coding(),
        *llobot.instructions.answering(),
    )

@lru_cache
def create(*, instructions: str = instructions(), **kwargs) -> Role:
    return llobot.roles.editor.create(instructions=instructions, **kwargs)

__all__ = [
    'description',
    'instructions',
    'create',
]

