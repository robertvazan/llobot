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
def standard(*,
    instructions: str = '',
    crammer: ExampleCrammer = llobot.crammers.examples.standard(),
) -> Role:
    def stuff(request: RoleRequest) -> Context:
        output = llobot.contexts.system(instructions)
        examples = request.memory.recent_examples(request.project, request.cutoff)
        output += crammer.cram(examples, request.budget - output.cost, request.context + output)
        return output
    return llobot.roles.create(stuff)

__all__ = [
    'standard',
]

