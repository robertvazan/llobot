from __future__ import annotations
from datetime import datetime
from functools import lru_cache
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.crammers.examples
import llobot.contexts
import llobot.experts
import llobot.experts.instructions

@lru_cache
def standard(*,
    instructions: Expert | str = '',
    crammer: ExampleCrammer = llobot.crammers.examples.standard(),
) -> Expert:
    instructions = llobot.experts.instructions.coerce(instructions)
    def stuff(request: ExpertRequest) -> Context:
        output = instructions(request)
        examples = request.memory.recent_examples(request.project, request.cutoff)
        output += crammer.cram(examples, request.budget - output.cost, request.context + output)
        return output
    return llobot.experts.create(stuff)

__all__ = [
    'standard',
]

