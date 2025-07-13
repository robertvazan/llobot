from __future__ import annotations
from functools import cache
from datetime import datetime
from llobot.contexts import Context
from llobot.chats import ChatBranch
from llobot.projects import Project
from llobot.roles.memory import RoleMemory
import llobot.contexts

class Role:
    # Returns the synthetic part of the prompt that is prepended to the user prompt.
    def stuff(self, *,
        memory: RoleMemory,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        return llobot.contexts.empty()

    def __call__(self, *,
        memory: RoleMemory,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        return self.stuff(memory=memory, prompt=prompt, project=project, cutoff=cutoff, budget=budget)

def create(function: Callable[[RoleMemory, ChatBranch, Project | None, datetime, int], Context]) -> Role:
    class LambdaRole(Role):
        def stuff(self, *,
            memory: RoleMemory,
            prompt: ChatBranch,
            project: Project | None,
            cutoff: datetime,
            budget: int,
        ) -> Context:
            return function(memory=memory, prompt=prompt, project=project, cutoff=cutoff, budget=budget)
    return LambdaRole()

@cache
def empty() -> Role:
    return Role()

__all__ = [
    'Role',
    'create',
    'empty',
]

