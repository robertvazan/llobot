from __future__ import annotations
from functools import lru_cache
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.roles import Role
from llobot.roles.requests import RoleRequest
import llobot.crammers.examples
import llobot.contexts
import llobot.roles

@lru_cache
def create(*,
    instructions: str = '',
    crammer: ExampleCrammer = llobot.crammers.examples.standard(),
) -> Role:
    def stuff(request: RoleRequest) -> Context:
        system = llobot.contexts.system(instructions)
        recent_examples = request.memory.recent_examples(request.project, request.cutoff)
        examples = crammer.cram(recent_examples, request.budget - system.cost, request.context + system)
        return system + examples
    return llobot.roles.create(stuff)

__all__ = [
    'create',
]

