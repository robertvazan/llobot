from __future__ import annotations
from functools import lru_cache
from llobot.roles import Role
from llobot.roles.requests import RoleRequest
import llobot.contexts
import llobot.roles

@lru_cache
def forced(instructions: str) -> Role:
    return llobot.roles.create(lambda _: llobot.contexts.system(instructions))

# This will go a little over the budget due to affirmation and message overhead.
@lru_cache
def trimming(instructions: str) -> Role:
    return llobot.roles.create(lambda request: llobot.contexts.system(instructions[:request.budget]))

@lru_cache
def optional(instructions: str) -> Role:
    context = llobot.contexts.system(instructions)
    def stuff(request: RoleRequest) -> Context:
        if context.cost > request.budget:
            return llobot.contexts.empty()
        return context
    return llobot.roles.create(stuff)

@lru_cache
def standard(instructions: str) -> Role:
    return optional(instructions)

def coerce(what: Role | str) -> Role:
    if isinstance(what, Role):
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

