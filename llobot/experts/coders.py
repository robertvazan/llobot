from __future__ import annotations
from functools import cache, lru_cache
from importlib import resources
from llobot.experts import Expert
import llobot.experts.editors

@cache
def standard_instructions() -> str:
    return (resources.files()/'coder.md').read_text().strip()

@lru_cache
def standard(*, instructions: Expert | str = standard_instructions(), **kwargs) -> Expert:
    return llobot.experts.editors.standard(instructions=instructions, **kwargs)

__all__ = [
    'standard_instructions',
    'standard',
]

