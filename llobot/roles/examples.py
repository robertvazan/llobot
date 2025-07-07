from __future__ import annotations
from datetime import datetime
from functools import lru_cache
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.roles import Role
from llobot.roles.requests import RoleRequest
import llobot.crammers.examples
import llobot.contexts
import llobot.roles
import llobot.roles.instructions

@lru_cache
def standard(*,
    instructions: Role | str = '',
    crammer: ExampleCrammer = llobot.crammers.examples.standard(),
) -> Role:
    instructions = llobot.roles.instructions.coerce(instructions)
    def stuff(request: RoleRequest) -> Context:
        output = instructions(request)
        examples = request.memory.recent_examples(request.project, request.cutoff)
        output += crammer.cram(examples, request.budget - output.cost, request.context + output)
        return output
    return llobot.roles.create(stuff)

__all__ = [
    'standard',
]

