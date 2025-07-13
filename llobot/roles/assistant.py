from __future__ import annotations
from datetime import datetime
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.roles import Role
from llobot.chats import ChatBranch
from llobot.projects import Project
from llobot.roles.memory import RoleMemory
import llobot.crammers.examples
import llobot.contexts

class Assistant(Role):
    _instructions: str
    _crammer: ExampleCrammer

    def __init__(self, *,
        instructions: str = '',
        crammer: ExampleCrammer = llobot.crammers.examples.standard(),
    ):
        self._instructions = instructions
        self._crammer = crammer

    def stuff(self, *,
        memory: RoleMemory,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        system = llobot.contexts.system(self._instructions)
        recent_examples = memory.recent_examples(project, cutoff)
        examples = self._crammer.cram(recent_examples, budget - system.cost, system)
        return system + examples

__all__ = [
    'Assistant',
]

