from __future__ import annotations
from functools import lru_cache
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.contexts
import llobot.experts

@lru_cache
def forced(instructions: str) -> Expert:
    return llobot.experts.create(lambda _: llobot.contexts.system(instructions))

# This will go a little over the budget due to affirmation and message overhead.
@lru_cache
def trimming(instructions: str) -> Expert:
    return llobot.experts.create(lambda request: llobot.contexts.system(instructions[:request.budget]))

@lru_cache
def optional(instructions: str) -> Expert:
    context = llobot.contexts.system(instructions)
    def stuff(request: ExpertRequest) -> Context:
        if context.cost > request.budget:
            return llobot.contexts.empty()
        return context
    return llobot.experts.create(stuff)

@lru_cache
def standard(instructions: str) -> Expert:
    return optional(instructions)

def coerce(what: Expert | str) -> Expert:
    if isinstance(what, Expert):
        return what
    if isinstance(what, str):
        return standard(what)
    raise TypeError(what)

__all__ = [
    'forced',
    'trimming',
    'optional',
    'standard',
    'coerce',
]

