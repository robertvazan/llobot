from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.roles import Role
from llobot.chats import ChatBranch
from llobot.projects import Project
from llobot.roles.memory import RoleMemory
import llobot.crammers.examples
import llobot.contexts
import llobot.roles

@lru_cache
def create(*,
    instructions: str = '',
    crammer: ExampleCrammer = llobot.crammers.examples.standard(),
) -> Role:
    def stuff(*,
        memory: RoleMemory,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        system = llobot.contexts.system(instructions)
        recent_examples = memory.recent_examples(project, cutoff)
        examples = crammer.cram(recent_examples, budget - system.cost, system)
        return system + examples
    return llobot.roles.create(stuff)

__all__ = [
    'create',
]

