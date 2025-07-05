from __future__ import annotations
from functools import cache, lru_cache
from llobot.experts import Expert
import llobot.experts.editors
import llobot.instructions

@cache
def standard_instructions() -> str:
    return llobot.instructions.compile(
        llobot.instructions.read('coder.md'),
        *llobot.instructions.coding(),
        *llobot.instructions.answering(),
    )

@lru_cache
def standard(*, instructions: Expert | str = standard_instructions(), **kwargs) -> Expert:
    return llobot.experts.editors.standard(instructions=instructions, **kwargs)

__all__ = [
    'standard_instructions',
    'standard',
]

